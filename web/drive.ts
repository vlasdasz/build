// Browser UI test lane driver. Builds the atomics wasm, serves dist with the
// isolation headers, and reads the suite report over the inspect WebSocket
// instead of scraping the console, so it drives any real installed browser
// with no automation protocol. See docs/ui-tests.md and docs/inspect.md.
//
//   bun build/web/drive.ts [--browser firefox|chrome|none] [--only "Name,Name"]
//                          [--port 44810] [--timeout 900] [--no-build]

import { parseArgs } from "node:util";
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { join, normalize } from "node:path";
import { tmpdir } from "node:os";

const { values: args } = parseArgs({
    options: {
        browser: { type: "string", default: "chrome" },
        only: { type: "string" },
        port: { type: "string", default: "44810" },
        timeout: { type: "string", default: "900" },
        "no-build": { type: "boolean", default: false },
    },
});

const root = normalize(join(import.meta.dir, "..", ".."));
const appDir = join(root, "test-game");
const dist = join(appDir, "dist");
const port = Number(args.port);

// rustc adds none of the threading flags itself, see docs/roadmap.md.
const RUSTFLAGS = [
    "-C target-feature=+atomics,+bulk-memory,+mutable-globals",
    "-C link-arg=--shared-memory",
    "-C link-arg=--import-memory",
    "-C link-arg=--max-memory=2147483648",
    "-C link-arg=--export=__wasm_init_tls",
    "-C link-arg=--export=__tls_size",
    "-C link-arg=--export=__tls_align",
    "-C link-arg=--export=__tls_base",
    "-C link-arg=--export=__heap_base",
    "-C link-arg=--export=__data_end",
].join(" ");

if (!args["no-build"]) {
    console.log("building atomics wasm with trunk");
    const build = Bun.spawnSync(["trunk", "build"], {
        cwd: appDir,
        env: {
            ...process.env,
            RUSTFLAGS,
            CARGO_UNSTABLE_BUILD_STD: "std,panic_abort",
        },
        stdout: "inherit",
        stderr: "inherit",
    });
    if (build.exitCode !== 0) {
        console.error("trunk build failed");
        process.exit(1);
    }
}

let browserProc: ReturnType<typeof Bun.spawn> | undefined;
let profileDir: string | undefined;
let appSocket: Bun.ServerWebSocket<unknown> | undefined;
let finished = false;
let pendingExit: number | undefined;

function finish(code: number) {
    if (finished) return;
    finished = true;
    browserProc?.kill();
    if (profileDir) rmSync(profileDir, { recursive: true, force: true });
    // Give the kill a moment so the browser does not outlive the server.
    setTimeout(() => process.exit(code), 500);
}

// Asks the app for a screenshot over the inspect socket before exiting, CI
// uploads it as the failure artifact. Falls through when the app is gone.
function failWithScreenshot(code: number) {
    if (finished) return;
    if (!appSocket || appSocket.readyState !== 1) return finish(code);
    pendingExit = code;
    appSocket.send('"Screenshot"');
    setTimeout(() => finish(code), 10_000);
}

process.on("SIGINT", () => finish(130));

// A browser aborts asset requests it no longer needs. The aborted stream
// surfaces as an async error that must not kill the driver mid run.
process.on("unhandledRejection", (err) => {
    console.log(`ignored async error: ${err}`);
});

const server = Bun.serve({
    port,
    fetch(req, server) {
        const url = new URL(req.url);

        if (url.pathname === "/te-inspect") {
            return server.upgrade(req) ? undefined : new Response("upgrade failed", { status: 400 });
        }

        if (url.pathname === "/te-panic" && req.method === "POST") {
            req.text().then((body) => {
                console.error(`APP PANIC: ${body}`);
                finish(1);
            });
            return new Response(null, { status: 204 });
        }

        let path = normalize(url.pathname);
        if (path.includes("..")) return new Response("forbidden", { status: 403 });
        if (path === "/") path = "/index.html";

        const file = Bun.file(join(dist, path));
        return file.exists().then((exists) => {
            if (!exists) return new Response("not found", { status: 404 });
            return new Response(file, {
                headers: {
                    // Workers with shared wasm memory need cross origin isolation.
                    "Cross-Origin-Opener-Policy": "same-origin",
                    "Cross-Origin-Embedder-Policy": "require-corp",
                    "Cache-Control": "no-store",
                },
            });
        });
    },
    error(err) {
        console.log(`server error: ${err}`);
        return new Response(null, { status: 500 });
    },
    websocket: {
        open(ws) {
            appSocket = ws;
            console.log("app connected to the inspect socket");
        },
        message(_ws, message) {
            const frame = JSON.parse(String(message));

            if (frame.TestResults) {
                const { total, failures } = frame.TestResults;
                for (const failure of failures) {
                    console.error(`TEST FAILED: ${failure.name}\n${failure.detail}`);
                }
                console.log(`TE_TEST_RESULT ${total} tests, ${failures.length} failed`);
                if (failures.length > 0) failWithScreenshot(1);
                else finish(0);
                return;
            }

            if (frame.Screenshot) {
                const shotDir = join(root, "target", "web-test");
                mkdirSync(shotDir, { recursive: true });
                const shot = join(shotDir, "ui-web-failure.png");
                writeFileSync(shot, Buffer.from(frame.Screenshot.png_base64, "base64"));
                console.log(`failure screenshot saved to ${shot}`);
                finish(pendingExit ?? 1);
                return;
            }

            console.log(`unexpected inspect frame: ${String(message)}`);
        },
        close() {
            appSocket = undefined;
            if (!finished) console.log("inspect socket closed");
        },
    },
});

let query = "?te_run_tests=1&te_inspect=1";
if (args.only) query += `&te_test_only=${encodeURIComponent(args.only)}`;
const url = `http://localhost:${server.port}/${query}`;

console.log(`serving ${dist} at ${url}`);

// A missing browser must fail the lane at once, a spawn error would
// otherwise surface as a silent hang until the timeout.
function browserBinary(name: string, candidates: (string | null)[]): string {
    const found = candidates.find((c) => c && existsSync(c));
    if (!found) {
        console.error(`${name} is not installed`);
        process.exit(1);
    }
    return found;
}

// Always a real installed browser, headed, with a throwaway profile.
// Headless reports different GPU state and Playwright ships patched builds,
// neither says anything about what users run.
if (args.browser === "firefox") {
    profileDir = mkdtempSync(join(tmpdir(), "te-firefox-"));
    writeFileSync(
        join(profileDir, "user.js"),
        [
            'user_pref("dom.webgpu.enabled", true);',
            'user_pref("browser.shell.checkDefaultBrowser", false);',
            'user_pref("browser.aboutwelcome.enabled", false);',
            'user_pref("datareporting.policy.dataSubmissionEnabled", false);',
            'user_pref("app.update.disabledForTesting", true);',
        ].join("\n"),
    );
    browserProc = Bun.spawn(
        [
            browserBinary("firefox", ["/Applications/Firefox.app/Contents/MacOS/firefox", Bun.which("firefox")]),
            "-no-remote",
            "-new-instance",
            "-profile",
            profileDir,
            "-width",
            "760",
            "-height",
            "760",
            url,
        ],
        { stdout: "ignore", stderr: "ignore" },
    );
} else if (args.browser === "chrome") {
    profileDir = mkdtempSync(join(tmpdir(), "te-chrome-"));
    browserProc = Bun.spawn(
        [
            browserBinary("chrome", [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                Bun.which("google-chrome"),
                Bun.which("chromium"),
            ]),
            `--user-data-dir=${profileDir}`,
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=760,860",
            "--new-window",
            url,
        ],
        { stdout: "ignore", stderr: "ignore" },
    );
} else if (args.browser !== "none") {
    console.error(`unknown browser: ${args.browser}`);
    finish(1);
}

setTimeout(() => {
    console.error(`no report after ${args.timeout} seconds`);
    failWithScreenshot(1);
}, Number(args.timeout) * 1000);
