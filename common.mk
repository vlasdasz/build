
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

clippy:
	cargo clippy -- -D clippy::pedantic -A clippy::module-name-repetitions -A clippy::must_use_candidate -A clippy::implicit-hasher -A clippy::missing_errors_doc -A clippy::semicolon_if_nothing_returned -A clippy::return_self_not_must_use -A clippy::default_trait_access -A clippy::needless_pass_by_value -A clippy::missing_panics_doc -A clippy::mismatched_target_os -A clippy::explicit-deref-methods -A clippy::cast-precision-loss -A clippy::module_inception

lint: clippy

order:
	taplo fmt; \
	cargo +nightly fmt --all; \
	make clippy; \
	typos; \
	cargo test; \
	cargo build --all
	    #	cargo machete; \

test:
	cargo test --all  && \
    echo debug test: OK && \
    cargo test --all --release && \
    echo release test: OK

deps:
	cargo install cargo-machete;\
    cargo install typos-cli;\
    cargo install taplo-cli

fly:
	./build/flight.sh

release:
	cargo build --release

run-release:
	cargo run --release

plus:
	cargo build --profile=release-plus

run-plus:
	cargo run --profile=release-plus