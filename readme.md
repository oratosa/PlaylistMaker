# PlaylistMaker
PlaylistMaker gets the track info broadcasted on [Weekend Sunshine](https://www4.nhk.or.jp/sunshine/66/) and creates a playlist on Spotify.

Those playlists are here: https://open.spotify.com/user/213qnu6e3ycwpsfevbtit2tjy?si=PKQUuNWhTSatT9xufyD60A

## How does it work?
This works weekly on Google Cloud Functions.

## How to test on the local environment
1. Load the environmental parameter

    source env.sh

2. Start a functions-framework

    functions-framework --target=$FUNCTION_TARGET --signature-type=$FUNCTION_SIGNATURE_TYPE

3. (On another terminal) Send a cloudevent

    curl localhost:8080 \
        -X POST \
        -H "Content-Type: application/json" \
        -H "ce-id: 123451234512345" \
        -H "ce-specversion: 1.0" \
        -H "ce-time: 2020-01-02T12:34:56.789Z" \
        -H "ce-type: google.cloud.pubsub.topic.v1.messagePublished" \
        -H "ce-source: //pubsub.googleapis.com/projects/MY-PROJECT/topics/MY-TOPIC" \
        -d '{
              "message": {
                "data": "d29ybGQ=",
                "attributes": {
                   "attr1":"attr1-value"
                }
              },
              "subscription": "projects/MY-PROJECT/subscriptions/MY-SUB"
            }'
    