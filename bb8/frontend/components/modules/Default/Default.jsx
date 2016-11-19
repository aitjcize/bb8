import React from 'react'

import uniqueId from 'lodash/uniqueId'
import { Validator } from 'jsonschema'

import Snackbar from 'material-ui/Snackbar'
import ActionDelete from 'material-ui/svg-icons/action/delete'
import { Card, CardHeader, CardMedia } from 'material-ui/Card'
import Divider from 'material-ui/Divider'
import FloatingActionButton from 'material-ui/FloatingActionButton'
import { ListItem } from 'material-ui/List'

import Rule from './Rule'
import ModuleInfos from '../../../constants/ModuleInfos.json'


class Default extends React.Component {
  constructor(props) {
    super(props)

    this.moduleId = 'ai.compose.router.core.default'

    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)
    this.loadFromJSON = this.loadFromJSON.bind(this)
    this.clear = this.clear.bind(this)

    this.state = {
      ruleInfos: [],
      snackbarOpen: false,
      snackbarMessage: '',
      hoverIndex: undefined,
    }
    this.rules = []
    this.idRule = {}

    this.defaultProps = {
      maxRules: 10,
      editorWidth: '30em',
    }
  }

  onAddClicked(type) {
    if (this.state.ruleInfos.length < this.props.maxRules) {
      this.setState(prevState => (
        { ruleInfos: prevState.ruleInfos.concat(
          [{ id: uniqueId('rules'), type }]) }
      ))
    }
  }

  onRemoveClicked(id) {
    this.setState(prevState => (
      { ruleInfos: prevState.ruleInfos.filter(x => x.id !== id) }
    ))
    delete this.rules[id]
  }

  clear() {
    this.rules = {}
    this.idRule = {}
    this.setState({
      ruleInfos: [],
      snackbarOpen: false,
      snackbarMessage: '',
      hoverIndex: undefined,
    })
  }

  toJSON() {
    const rules = []
    for (const info of this.state.ruleInfos) {
      if (this.rules[info.id].valid()) {
        rules.push(this.rules[info.id].toJSON())
      }
    }
    const obj = { links: rules }
    const v = new Validator()
    const schema = ModuleInfos[this.moduleId].schema
    const result = v.validate(obj, schema)
    if (!result.valid) {
      this.setState({
        snackbarOpen: true,
        snackbarMessage: 'Critial: rule validation failed',
      })
    }
    return obj
  }

  fromJSON(rules) {
    const idRule = {}
    const ruleInfos = []
    for (const link of rules.links) {
      const id = uniqueId('rules')
      idRule[id] = link
      ruleInfos.push({ id, type: link.rule.type })
    }
    this.setState({ ruleInfos })
    this.idRule = idRule
  }

  loadFromJSON(rule, id) {
    this.rules[id] = rule
    if (this.idRule[id]) {
      rule.fromJSON(this.idRule[id])
      delete this.idRule[id]
    }
  }

  render() {
    const showAddButton = (
      this.state.ruleInfos.length < this.props.maxRules)

    return (
      <div>
        {
        this.state.ruleInfos.map((info, index) => {
          const ruleContent = (
            <Rule
              type={info.type}
              ref={(r) => { this.loadFromJSON(r, info.id) }}
            />
          )
          return (
            <div
              key={info.id}
              onMouseEnter={() => {
                this.setState({ hoverIndex: index })
              }}
              onMouseLeave={() => {
                this.setState({ hoverIndex: undefined })
              }}
              style={{
                margin: '1.4em',
                position: 'relative',
              }}
            >
              {ruleContent}
              {this.state.hoverIndex === index &&
              <FloatingActionButton
                mini
                secondary
                onClick={() => { this.onRemoveClicked(info.id) }}
                style={{ position: 'absolute', left: -20, top: -20 }}
              >
                <ActionDelete />
              </FloatingActionButton>
              }
            </div>
          )
        })
        }
        {showAddButton &&
        <Card style={{ width: this.props.editorWidth, margin: '1.4em' }}>
          <CardHeader
            title="Add a new rule"
            style={{ fontWeight: '900' }}
          />
          <CardMedia>
            <Divider />
            <ListItem
              primaryText="Keyword / Regular Expression"
              onClick={() => { this.onAddClicked('regexp') }}
            />
            <Divider />
            <ListItem
              primaryText="Location"
              onClick={() => { this.onAddClicked('location') }}
            />
          </CardMedia>
        </Card>
        }
        <Snackbar
          open={this.state.snackbarOpen}
          message={this.state.snackbarMessage}
          autoHideDuration={3000}
          onRequestClose={() => { this.setState({ snackbarOpen: false }) }}
        />
      </div>
    )
  }

}

Default.propTypes = {
  maxRules: React.PropTypes.number.isRequired,
  editorWidth: React.PropTypes.string.isRequired,
}

export default Default
