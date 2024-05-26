#!/bin/bash

# Install Java 17
apt update
apt install -y openjdk-17-jdk curl sudo unzip

# Set JAVA_HOME environment variable
echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" >> ~/.bashrc
echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> ~/.bashrc

# Source the .bashrc file to apply changes
source ~/.bashrc

# Verify the installation
java -version

# Provide instruction for updating Gradle if necessary
echo "If you encounter issues with Gradle, ensure your Gradle wrapper is updated to a compatible version in gradle-wrapper.properties"
echo "Example:"
echo "distributionUrl=https\\://services.gradle.org/distributions/gradle-7.3.3-bin.zip"
