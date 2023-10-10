#!/bin/bash

set -e

PROJECT_NAME="Money"
SCHEME_NAME="Money Release"

source env.sh

EXPORT_OPTIONS_PLIST="export.plist"
ARCHIVE_PATH="build/$PROJECT_NAME.xcarchive"
IPA_PATH="build/$SCHEME_NAME.ipa"


make ios

cd mobile/iOS

rm -rf build

# Clean build folder
xcodebuild clean -project "$PROJECT_NAME.xcodeproj" -scheme "$SCHEME_NAME" -configuration Release

# Build project
xcodebuild -project $PROJECT_NAME.xcodeproj -scheme "$SCHEME_NAME" \
-sdk iphoneos -configuration Release archive -archivePath $ARCHIVE_PATH
# Export IPA
xcodebuild -exportArchive -archivePath $ARCHIVE_PATH -exportOptionsPlist "$EXPORT_OPTIONS_PLIST" -exportPath "build"

xcrun altool --upload-app -f "$IPA_PATH" -u 146100@gmail.com -p "$FLIGHT_PASS" --type ios
