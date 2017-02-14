# Bot Definition

This directory contains definitions of all compose.ai bot in JSON format.

## Edit


SnipMate is a wonderful tool that provides snippet expansion for fast editing.
We generate our own snippets from json schemas for easy editing of bot files.

### Installation

Please follow the [instruction in the SnipMate
repo](https://github.com/garbas/vim-snipmate) to install snipmate first. Then
run `bb8/scripts/generate_snippets.py` which generate a `json.snippets` for the
JSON format.

After you have `json.snippets`, copy it to
`~/.vim/bundle/vim-snippets/snippets` and you are all set.

### Usage

The rules for the snippet naming is as follows:

1. The snippet expansion keyword is usually the same as the JSON key name.

   First we open an emtpy `test.bot` file. Type `bot<tab>` then it expands to
   
   ```javascript
   {
     "name": "string",
     "session_timeout": integer,
     "description": "string",
     "interaction_timeout": 120,
     "admin_interaction_timeout": 10,
     "ga_id": "opt;string",
     "nodes": objects
   }
   ```
   
   Press `<tab>` and `<shift> + <tab>` to jump between different placeholders.
   Placeholders with `opt;` prefix means that the key is optional and can be
   deleted.
   
   Next we navigate to the `nodes` value, and type `nodes<tab>`:
   
   ```javascript
   {
     "name": "string",
     "session_timeout": integer,
     "description": "string",
     "interaction_timeout": 120,
     "admin_interaction_timeout": 10,
     "ga_id": "opt;string",
     "nodes": nodes<tab>
   }
   ```
   
   Which then expand to:
   
   ```javascript
   {
     "name": "string",
     "session_timeout": integer,
     "description": "string",
     "interaction_timeout": 120,
     "admin_interaction_timeout": 10,
     "ga_id": "opt;string",
     "nodes": {
       "Start": object,
       "Root": object,
       "RootRouter": object
     }
   }
   ```

2. The array item expansion keyword is the `${keyname}.items`. For example, if
   you see:

   ```javascript
   {
     "on_error": object,
     "links": array
   }
   ```
   
   Telling you that `links` is a array, then the array item can be expanded with
   the keyword `links.item`:
   
   ```javascript
   {
     "on_error": object,
     "links": array
     "links": [
       links.item<tab>
     ]
   }
   ```

You get the point. You can look at `json.snippets` to find out more.
