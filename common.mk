
ios:
	rust ./build/ios/build-project.rs

ios-lib:
	rust ./build/ios/build-lib.rs

android:
	rust ./build/build.rs android

android-emu:
	HILEN_ANDROID_ABI=arm64 rust ./build/build.rs android

test:
	cargo test --all
	echo debug test: OK
	cargo test --all --release
	echo release test: OK

fly:
	rust ./build/ios/flight.rs

profile:
	rust ./build/scripts/profile.rs

pr:
	gh pr create --fill

fmt:
	cargo +nightly fmt --all

fmt-check:
	cargo +nightly fmt --all -- --check

updates:
	cargo install cargo-upgrades --locked
	cargo upgrades

# Desktop release. `make patch` or `make minor` tags and pushes, CI builds
# from the tag with the release-* targets, one platform per runner. Every
# script reads Cargo.toml and the [release] table of hilen.toml.
patch:
	rust ./build/release/tag.rs patch

minor:
	rust ./build/release/tag.rs minor

release-mac:
	rust ./build/release/mac.rs

release-win:
	rust ./build/release/win.rs

release-linux:
	rust ./build/release/linux.rs

manifest:
	rust ./build/release/manifest.rs

upload:
	rust ./build/release/upload.rs
