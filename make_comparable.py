#!/usr/bin/env python3
import sys
import json
from datetime import datetime

def normalize_photo_metadata(data):
    """Normalize photo metadata for consistent comparison"""
#     print("normalize_photo_metadata(data=", data, ")", file=sys.stderr)

    if 'photo' in data:
        photo = data['photo']
        # Remove orientationV2 as it varies between API versions
        if 'orientationV2' in photo:
            del photo['orientationV2']

        # Convert orientation string values to numeric
        if 'orientation' in photo:
            try:
                photo['orientation'] = int(photo['orientation'])
            except (ValueError, TypeError):
                # If conversion fails, remove orientation
                del photo['orientation']

    if 'reactions' in data:
        del data['reactions']

    return data


def main():
    print("---- make_comparable.py ---", file=sys.stderr)
    for line in sys.stdin:
        parts = line.rstrip().split('\t')

#         print("DEBUG: Line parts:", file=sys.stderr)
#         for i, part in enumerate(parts):
#             print(f"Part {i}: {part}", file=sys.stderr)
#         print("---", file=sys.stderr)

        if len(parts) >= 19:  # Metadata is last column
            try:
#                 metadata = json.loads(parts[19])
#                 # Normalize photo metadata
#                 metadata = normalize_photo_metadata(metadata)
#                 # Reconstruct line with normalized metadata
#                 parts[19] = json.dumps(metadata, sort_keys=True)
#                 print('\t'.join(parts))

                metadata = json.loads(parts[19])

                # Extract QuickXorHash from metadata
                hash_value = metadata.get('file', {}).get('hashes', {}).get('quickXorHash', 'N/A')

                # Adjust prevision of Modified date
                normalized_date = datetime.fromisoformat(
                    metadata["fileSystemInfo"]["lastModifiedDateTime"].replace("Z","+00:00")
                )
                normalized_date = normalized_date.strftime('%Y-%m-%dT%H:%M:%SZ')

                # Output just critical fields
                out_parts = [
                    parts[1],  # Path
                    normalized_date,  # Modified date
                    parts[4],  # Size in bytes
                    hash_value # QuickXorHash
                ]
                print('\t'.join(out_parts))

            except json.JSONDecodeError:
                print(line.rstrip())
        else:
            print(line.rstrip())


if __name__ == '__main__':
    main()
