
all: desktop

clean:
	cargo clean

everything: order desktop ios android

desktop:
	./build/build.sh

ios:
	./build/build.sh ios

lipo:
	cargo lipo

android:
	./build/build.sh android

lint:
	cargo clippy -- \
	-D clippy::pedantic \
	-A clippy::too_many_arguments \
	-A clippy::no-effect-underscore-binding \
	-A clippy::unnecessary_box_returns \
	-A clippy::module-name-repetitions \
	-A clippy::must_use_candidate \
	-A clippy::missing_errors_doc \
	-A clippy::return_self_not_must_use \
	-A clippy::needless_pass_by_value \
	-A clippy::missing_panics_doc \
	-A clippy::mismatched_target_os \
	-A clippy::explicit-deref-methods \
	-A unexpected_cfgs \
	-A clippy::module_inception

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
	./build/flight.sh

profile:
	./build/profile.sh

release:
	cargo build --release

run-release:
	cargo run --release

plus:
	cargo build --profile=release-plus

run-plus:
	cargo run --profile=release-plus

.PHONY: test clippy
