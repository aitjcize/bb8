z# Database Schema


## Account
```javascript
{
  "id": 1,
  "name": "user name",
  "email": "user@somedomain.com",
  "passwd": "password hash",
  "bots": [bot_id_1, bot_id_2 ...]
}
```

## Node
```javascript
{
  "id": 1,
  "bot_id": 1,
  "content": {
    "msg_ids": [1, 2 ..], // list of message ID
    "url": "http://somedoamin.com?param1=%(param1)s&param2=%(param2)s",
    "filename": "/path/to/content_script.js"
  },
  "parser": {
    "module_id": 1,
    "config": {...}
  },
  "action_map": {  // action_id to end node mapping
    "content.search": {
      "message": "msg",
      "end_node_id": 1
    },
    ...
    "error": {
      "message": "msg",
      "end_node_id": self.id
    },
    "default": {  // parse ok, but no handler set
      "message": "msg",
      "end_node_id": 2
    }
  }
}
```

## Module
Parses user input as action.

```javascript
{
  "id": 1,
  "name": "Module Name",
  "parser_filename": "/path/to/parser.py",
  "ui_filename": "/path/to/react/ui/module.js",
  "actions": [
    {"name": "Search Product", "id": "content.search"},
    ...
  ],
  "parameter": ["search_term", ...],  // parameter for next node
}
```

## Message

```javascript
{
  "id": 1,
  "type": 0,
  "content": {...}  // content json template depends on type
}
```

*type* enum:

- 0: text only
- 1: card

### text content schema
```javascript
{
  "text": "text message"
}
```

### card content schema
```javascript
{
   "title": "title",
   "subtitle": "subtitle",
   "image_url": "URL to image",
   "item_url": "URL that is opened when bubble is tapped",
   "options": [
     {
       "type": "web_url" or "postback",
       "title": "button title",
       "url": "URL",
       "payload": "{\"node_id\": {{node_id}}, \"payload\": \"action string\"}
     },
     ...
     {}
   ]
}
```

## Bot
```javascript
{
  "platforms": [platform.id ...],
  "interaction_timeout": 600,  // broadcast only if user is idle for X secs
  "session_timeout": 86400,  // reset user state if timeout
  "root_node_id": 0,
  "start_node_id": 1,
  "orphan_node_ids": [...]  // list of orphan node that does not have parent
}
```

## Platform
```javascript
{
  "id": 1,
  "type": 0,
  "config": {...}  // config in json format
}
```
*type* enum:

- 0: facebook
- 1: line
- 2: wechat

## Bot User
```javascript
{
  "id": 1,
  "platform_type": type,  // same as Platform.type enum
  "platform_user_id": id,  // ID specific to platform: Facebook/LINE user ID
  "session": [node_id_1, node_id_2 ... ], // a stack
}
```

## Collected Data
```javascript
{
  "id": 1,
  "account_id": 2,
  "bot_user_id": 3,
  "key": "key",
  "value": "value"
}
```

## Conversation
```javascript
{
  "id": 1,
  "bot_id": 1,
  "bot_user_id": 1,
  "sender": 0,
  "msg": { ... }  // message json object
}
```
*sender* enum:

- 0: bot
- 1: user

## Events
```javascript
{
  "id": 1,
  "bot_id": 1,
  "bot_user_id": 1,
  "event_name": "event name",
  "event_value": "value",
}
```

*event_name* value:

- click_url: url
- action: action_name
- enter_node: node_id
