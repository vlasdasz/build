
ios:
	./build/ios/build-project.sh

android:
	./build/build.sh android

test:
	cargo test --all
	echo debug test: OK
	cargo test --all --release
	echo release test: OK

fly:
	./build/ios/flight.sh

profile:
	./build/scripts/profile.sh

pr:
	gh pr create --fill

fmt:
	cargo +nightly fmt --all

updates:
	cargo install cargo-upgrades --locked
	cargo upgrades
