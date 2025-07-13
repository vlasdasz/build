
clean:
	cargo clean

desktop:
	./build/build.sh

ios:
	./build/build.sh ios

lipo:
	cargo lipo

android:
	./build/build.sh android

test:
	cargo test --all
	echo debug test: OK
	cargo test --all --release
	echo release test: OK

deps:
	cargo install cargo-machete;\
    cargo install typos-cli;\
    cargo install taplo-cli

fly:
	./build/scripts/flight.sh

profile:
	./build/scripts/profile.sh

release:
	cargo build --release

run-release:
	cargo run --release

plus:
	cargo build --profile=release-plus

run-plus:
	cargo run --profile=release-plus

pr:
	gh pr create --fill

r:
	cargo run --release

fmt:
	cargo +nightly fmt --all

.PHONY: test clippy
