import React from 'react'

import { Validator } from 'jsonschema'

import {
  Card,
  CardText,
  CardHeader,
  CardTitle,
  CardActions,
} from 'material-ui/Card'

import MenuItem from 'material-ui/MenuItem'
import Divider from 'material-ui/Divider'
import TextField from 'material-ui/TextField'
import SelectField from 'material-ui/SelectField'
import FlatButton from 'material-ui/FlatButton'

import {
  CarouselMessage,
  ImageMessage,
  TextCardMessage,
} from './Message'

import BotSchema from '../../schema/bot.schema.json'


const styles = {
  container: {
  },
  cardText: {
    paddingRight: '3em',
    paddingBottom: '3em',
  },
  header: {
    lineHeight: '1.5em',
    margin: '1em 0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  textFieldInput: {
    padding: '0 1em',
    boxSizing: 'border-box',
    textAlign: 'center',
  },
  errorMessageContainer: {
    margin: '1em',
    maxWidth: '50%',
  },
  errorMessageInputContainer: {
    display: 'flex',
    alignItems: 'center',
    padding: '0 .5em',
    boxSizing: 'border-box',
  },
  errorMessageInputField: {
    marginLeft: '.25em',
  },
  formWrapper: {
    width: '50%',
    display: 'flex',
    flexDirection: 'column',
  },
  formRow: {
    display: 'flex',
  },
}

const cardTypeEnum = {
  Disable: 0,
  Text: 1,
  Image: 2,
  Carousel: 3,
}

const BOT_TEMPLATE = {
  bot: {
    name: 'No name',
    description: '',
    interaction_timeout: 120,
    admin_interaction_timeout: 10,
    session_timeout: 0,
    ga_id: '',
    settings: {
      get_start_button: { message: { text: 'Hi' } },
      persistent_menu: [
        {
          type: 'web_url',
          title: 'Powered by Compose.ai',
          url: 'http://compose.ai',
        },
      ],
    },
    nodes: {
      Start: {
        name: 'Start',
        expect_input: false,
        next_node_id: 'Root',
        module: {
          id: 'ai.compose.content.core.message',
          config: {},
        },
      },
      Root: {
        name: 'Root',
        description: 'Main bot operation node',
        expect_input: false,
        next_node_id: 'RootRouter',
        module: {
          id: 'ai.compose.content.core.message',
          config: {
            messages: [
              {
                text: 'What can I do for you?',
              },
            ],
            quick_replies: [],
          },
        },
      },
      RootRouter: {
        name: 'RootRouter',
        expect_input: true,
        next_node_id: 'Root',
        module: {
          id: 'ai.compose.router.core.default',
          config: {
            links: [
              {
                rule: {
                  type: 'regexp',
                  params: ['(?i)contact'],
                },
                ack_message: '',
                end_node_id: 'ContactInfo',
              },
            ],
            on_error: {
              ack_message: [],
              end_node_id: 'RootRouter',
            },
          },
        },
      },
      ContactInfo: {
        name: 'ContactInfo',
        expect_input: false,
        next_node_id: 'Root',
        module: {
          id: 'ai.compose.content.core.message',
          config: {
            messages: [],
          },
        },
      },
    },
  },
}

class LandingPage extends React.Component {

  constructor(props) {
    super(props)

    this.editors = []
    this.toBot = this.toBot.bind(this)

    this.state = {
      intro: '',
      content: [
        {
          requestText: 'Feature',
          type: cardTypeEnum.Carousel,
        },
        {
          requestText: 'Demo',
          type: cardTypeEnum.Carousel,
        },
        {
          requestText: 'Product',
          type: cardTypeEnum.Carousel,
        },
      ],
      contacts: {
        name: '',
        email: '',
        phone: '',
        openHour: '',
        website: '',
      },
      errorMessage: ['', '', '', '', ''],
    }
  }

  toBot() {
    const botfile = Object.assign({}, BOT_TEMPLATE)

    // Bot name
    botfile.bot.name = this.state.contacts.name || 'No name'
    botfile.bot.description = this.state.contacts.website

    // Start node
    botfile.bot.nodes.Start.module.config.messages = [
      { text: this.state.intro },
    ]

    for (let i = 0; i < this.state.content.length; i += 1) {
      if (this.editors[i].valid()) {
        const section = this.state.content[i]

        // Root quick replies
        botfile.bot.nodes.Root.module.config.quick_replies.push({
          content_type: 'text',
          title: section.requestText,
        })

        // Links
        botfile.bot.nodes.RootRouter.module.config.links.push({
          rule: {
            type: 'regexp',
            params: [`(?i)${section.requestText}`],
          },
          end_node_id: section.requestText,
        })

        // Nodes
        botfile.bot.nodes[section.requestText] = {
          name: section.requestText,
          expect_input: false,
          next_node_id: 'Root',
          module: {
            id: 'ai.compose.content.core.message',
            config: {
              messages: [
                this.editors[i].toJSON(),
              ],
            },
          },
        }
      }
    }

    // Error messages
    botfile.bot.nodes.RootRouter.module.config.on_error.ack_message = []
    for (const msg of this.state.errorMessage) {
      if (msg) {
        botfile.bot.nodes.RootRouter.module.config.on_error.ack_message.push(msg)
      }
    }

    // Contact info
    botfile.bot.nodes.ContactInfo.module.config.messages = [
      {
        text: 'You can reach us through the following information:',
      },
      {
        text: `Email: ${this.state.contacts.email}\nPhone: ${this.state.contacts.phone}`,
      },
    ]

    const v = new Validator()
    const result = v.validate(botfile, BotSchema)
    if (!result.valid) {
      // Show error message in snackbar
    }
    return botfile
  }

  render() {
    const { content, errorMessage } = this.state
    const introMaxLength = 150

    return (
      <Card
        expandable
        initiallyExpanded
        style={styles.container}
      >
        <CardHeader
          title="Quick Start"
          subtitle="subtitle"
        />
        <CardTitle
          title="Intro"
          subtitle="a simple welcome message to tell your costomer who you are."
        />
        <CardText
          style={styles.cardText}
        >
          <div
            style={{
              ...styles.formWrapper,
              ...{ alignItems: 'flex-end' },
            }}
          >
            <TextField
              multiLine
              rows={3}
              value={this.state.intro}
              fullWidth
              onChange={(e) => {
                if (e.target.value.length <= introMaxLength) {
                  this.setState({ intro: e.target.value })
                }
              }}
            />
            <span
              style={{
                color: '#bbb',
                fontStyle: 'italic',
                padding: '0 1.5em',
              }}
            >
              {`${this.state.intro.length}/${introMaxLength}`}
            </span>
          </div>
        </CardText>
        <Divider />
        <CardTitle
          title="Content"
          subtitle="description"
          showExpandableButton
          actAsExpander
        />
        <CardText
          expandable
          style={styles.cardText}
        >
          {
          content.map((b, idx) => (
            <div style={styles.items} key={idx}>
              <div style={styles.header}>
                <div>
                  When customer says
                  <TextField
                    onChange={(e) => {
                      const stateContent = this.state.content
                      stateContent[idx].requestText = e.target.value
                      this.setState({ content: stateContent })
                    }}
                    value={this.state.content[idx].requestText}
                    inputStyle={styles.textFieldInput}
                    style={{ width: 'auto', minWidth: '10em' }}
                  />
                  ,
                  <br />
                  Do response:
                </div>
                <div>
                  <SelectField
                    floatingLabelText="Card Type"
                    value={b.type || cardTypeEnum.Text}
                    onChange={(e, selectIdx, selectPayload) => {
                      this.setState((state) => {
                        const stateContent = state.content
                        stateContent[idx].type = selectPayload
                        return {
                          ...state,
                          content: stateContent,
                        }
                      })
                    }}
                    style={{ width: 'auto' }}
                    labelStyle={{ paddingRight: '1.5em', margin: '0 3em' }}
                  >
                    <MenuItem value={cardTypeEnum.Text} primaryText="Text Card" />
                    <MenuItem value={cardTypeEnum.Image} primaryText="Image" />
                    <MenuItem value={cardTypeEnum.Carousel} primaryText="Carousel" />
                    <Divider />
                    <MenuItem value={cardTypeEnum.Disable} primaryText="Disable" />
                  </SelectField>
                </div>
              </div>
              {
                b.type === cardTypeEnum.Text &&
                <TextCardMessage
                  ref={(m) => {
                    this.editors[idx] = m
                  }}
                />
              }
              {
                b.type === cardTypeEnum.Image &&
                <ImageMessage
                  ref={(m) => {
                    this.editors[idx] = m
                  }}
                />
              }
              {
                b.type === cardTypeEnum.Carousel &&
                <CarouselMessage
                  ref={(m) => {
                    this.editors[idx] = m
                  }}
                />
              }
            </div>
          ))
          }
        </CardText>
        <Divider />
        <CardTitle
          title="Contacts"
          subtitle="how do your customers reach you"
        />
        <CardText
          style={styles.cardText}
        >
          <div style={styles.formWrapper}>
            <div style={styles.formRow}>
              <TextField
                value={this.state.contacts.name}
                onChange={(e) => {
                  const contacts = this.state.contacts
                  contacts.name = e.target.value
                  this.setState({ ...this.state, contacts })
                }}
                floatingLabelText="Business name"
                fullWidth
              />
            </div>
            <div style={styles.formRow}>
              <TextField
                value={this.state.contacts.email}
                onChange={(e) => {
                  const contacts = this.state.contacts
                  contacts.email = e.target.value
                  this.setState({ ...this.state, contacts })
                }}
                floatingLabelText="Email"
                fullWidth
              />
              <TextField
                value={this.state.contacts.phone}
                onChange={(e) => {
                  const contacts = this.state.contacts
                  contacts.phone = e.target.value
                  this.setState({ ...this.state, contacts })
                }}
                floatingLabelText="Phone number"
                fullWidth
              />
            </div>
            <div style={styles.formRow}>
              <TextField
                value={this.state.contacts.openHour}
                onChange={(e) => {
                  const contacts = this.state.contacts
                  contacts.openHour = e.target.value
                  this.setState({ ...this.state, contacts })
                }}
                floatingLabelText="Open hour"
                fullWidth
              />
              <TextField
                value={this.state.contacts.website}
                onChange={(e) => {
                  const contacts = this.state.contacts
                  contacts.website = e.target.value
                  this.setState({ ...this.state, contacts })
                }}
                floatingLabelText="Website"
                fullWidth
              />
            </div>
          </div>
        </CardText>
        <Divider />
        <CardTitle
          title="Error messages"
          subtitle="description"
        />
        <CardText
          style={styles.cardText}
        >
          <div style={styles.formWrapper}>
            {
            errorMessage.map((b, idx) => (
              <div key={idx} style={styles.errorMessageInputContainer}>
                <span style={{ fontStyle: 'italic', color: '#bbb' }}>
                  {`${idx + 1}. `}
                </span>
                <TextField
                  fullWidth
                  value={this.state.errorMessage[idx]}
                  onChange={(e) => {
                    const value = e.target.value
                    this.setState((state) => {
                      const errMsgs = state.errorMessage
                      errMsgs[idx] = value
                      return {
                        ...state,
                        errorMessage: errMsgs,
                      }
                    })
                  }}
                  style={styles.errorMessageInputField}
                />
              </div>
            ))
            }
          </div>
        </CardText>
        <CardActions>
          <FlatButton
            label="save"
            onClick={() => {
              this.toBot()
            }}
          />
        </CardActions>
      </Card>
    )
  }
}

export default LandingPage
