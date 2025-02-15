#!/bin/bash
set -eox pipefail

source env.sh

EXPORT_OPTIONS_PLIST="export.plist"
ARCHIVE_PATH="build/$PROJECT_NAME.xcarchive"
IPA_PATH="build/$PROJECT_NAME.ipa"

make ios

cd mobile/iOS

rm -rf build

echo "PROJECT_NAME: $PROJECT_NAME"
echo "ARCHIVE_PATH: $ARCHIVE_PATH"
echo "IPA_PATH: $IPA_PATH"

# Clean build folder
xcodebuild clean -project "$PROJECT_NAME.xcodeproj" -scheme "$PROJECT_NAME" -configuration Release

echo clean: OK

# Build project
xcodebuild -project "$PROJECT_NAME".xcodeproj -scheme "$PROJECT_NAME" \
  -sdk iphoneos -configuration Release archive -archivePath "$ARCHIVE_PATH"

echo build: OK

# Export IPA
xcodebuild -exportArchive -archivePath "$ARCHIVE_PATH" -exportOptionsPlist "$EXPORT_OPTIONS_PLIST" -exportPath "build"

echo export: OK

xcrun altool --upload-app -f "$IPA_PATH" -u 146100@gmail.com -p "$FLIGHT_PASS" --type ios

echo upload: OK
