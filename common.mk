
ios:
	SDKROOT=$(xcrun --sdk iphoneos --show-sdk-path) CFLAGS="" ./build/build.sh ios

android:
	./build/build.sh android

test:
	cargo test --all
	echo debug test: OK
	cargo test --all --release
	echo release test: OK

fly:
	SDKROOT=$(xcrun --sdk iphoneos --show-sdk-path) CFLAGS="" ./build/scripts/flight.sh

profile:
	./build/scripts/profile.sh

pr:
	gh pr create --fill

fmt:
	cargo +nightly fmt --all

updates:
	cargo install cargo-upgrades --locked
	cargo upgrades
