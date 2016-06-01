# Database Schema

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
Life cycle of a node:

1. Check if user has been idle for `session_timeout` seconds. If yes, clear the
   user session stack entirely. Push `start_node_id` onto session stack.

2. Show message of this node based on the output of content module. The
   parameter of content module is the `[action, variables...]` of the previous
   node. Example content modules:
   - Fixed message: display a list of pre-defined messages. The configuration
     requires specifying a list of msg_ids.
   - URL Query: e.g. search for product catalogue base on the user input
     (variables). The configuration requires specifiy query url template.

3. User input. A user input could either be a regular text message or a payload
   sent by pressing a button.

4. If user input payload contains a `stored_node_id` != `active_node_id`. Then
   unconditionally jump to the `stored_node_id` without pushing current session
   onto session stack.

5. Call the root node parser module to parser global commands from user input.
   If there is a match on the global command action:
   1. Push current user session (active `node_id`) onto session stack.
   2. Jump to corresponding node.

6. Call the parser module to parser the user's input. The parser module takes
   configurationl and generates:
  - `action_id`: e.g. `content.search`
  - `variables`: a dictionary. e.g. `{'search_term': 'watch', 'max_result': 5}`

7. Pop current session, push `end_node_id` onto session stack.

8. Goto 1

```javascript
{
  "id": 1,
  "bot_id": 1,
  "content": {
    "module_id": 1,
    "config": {...}
  },
  "parser": {
    "module_id": 1,
    "config": {...}
  },
  "linkage": {  // action_id to end node mapping
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
  },
}
```

## Contend Module
Takes input parameter (output variables of parser module) and render message.

```javascript
{
  "id": 1,
  "name": "Module Name",
  "content_filename": "/path/to/content.py",
  "ui_filename": "/path/to/react/ui/module.js",
}
```

## Parser Module
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
  "variables": [
      {
        "name": "search_term",
        "type": "string",
        "description": "Search term",
      }, ...
  ],  // used as parameter for next node
}
```
*type*
- bool
- number
- string

## Message

```javascript
{
  "id": 1,
  "bot_id": 0,
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
       "payload": "{\"node_id\": {{node_id}}, \"payload\": \"action string\"}"
     },
     ...
     {}
   ]
}
```

## Bot
In event of incoming broadcast message. Check if user has been idle for
`interaction_timeout`. If yes, send the broadcast message directly. The
broadcast message should contain notice of itself being an out-of-context
message to prevent user for consuing with current flow.

If a user has not been interacting with a bot for `session_timeout`, clear the
user session stack entirely.

```javascript
{
  "description": "description",
  "platforms": [platform.id ...],
  "interaction_timeout": 120,  // broadcast only if user is idle for X secs
  "session_timeout": 86400,  // reset user state if timeout
  "root_node_id": 0,
  "start_node_id": 1,
  "orphan_node_ids": [...]   // list of orphan node that does not have parent
}
```

## Platform
```javascript
{
  "id": 1,
  "bot_id": 0,
  "type": 0,
  "provider_ident": "facebook_page_id or line_mid",
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
  "session_stack": [node_id_1, node_id_2 ... ], // a stack
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
  "event_value": "value"
}
```

*event_name* value:

- click_url: url
- action: action_name
- enter_node: node_id
