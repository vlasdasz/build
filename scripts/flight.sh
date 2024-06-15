#!/bin/bash
set -eox pipefail
source env.sh

EXPORT_OPTIONS_PLIST="export.plist"
ARCHIVE_PATH="build/$PROJECT_NAME.xcarchive"
IPA_PATH="build/$IOS_RELEASE_SCHEME.ipa"

make ios

cd mobile/iOS

rm -rf build

echo "PROJECT_NAME: $PROJECT_NAME"
echo "IOS_RELEASE_SCHEME: $IOS_RELEASE_SCHEME"
echo "ARCHIVE_PATH: $ARCHIVE_PATH"
echo "IPA_PATH: $IPA_PATH"

# Clean build folder
xcodebuild clean -project "$PROJECT_NAME.xcodeproj" -scheme "$IOS_RELEASE_SCHEME" -configuration Release

# Build project
xcodebuild -project "$PROJECT_NAME".xcodeproj -scheme "$IOS_RELEASE_SCHEME" \
    -sdk iphoneos -configuration Release archive -archivePath "$ARCHIVE_PATH"

# Export IPA
xcodebuild -exportArchive -archivePath "$ARCHIVE_PATH" -exportOptionsPlist "$EXPORT_OPTIONS_PLIST" -exportPath "build"

xcrun altool --upload-app -f "$IPA_PATH" -u 146100@gmail.com -p "$FLIGHT_PASS" --type ios
