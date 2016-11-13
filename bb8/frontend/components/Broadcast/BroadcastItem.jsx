import React from 'react'
import Moment from 'moment'
import FlatButton from 'material-ui/FlatButton'
import Divider from 'material-ui/Divider'
import Paper from 'material-ui/Paper'
import {
  Card,
  CardActions,
  CardHeader,
  CardText
} from 'material-ui/Card'

import BroadcastEditor from './BroadcastEditor'

const styles = {
  container: {
    overflow: 'hidden',
  },
  paper: {
    borderRadius: 0,
    marginLeft: '1em',
    marginRight: '1em',
    transition: '.24s ease-out',
  },
  isFirst: {
    marginTop: '1em',
    borderRadius: '2px 2px 0 0',
  },
  isLast: {
    marginBottom: '1em',
    borderRadius: '0 0 2px 2px',
  },
  isExpanded: {
    marginTop: '.5em',
    marginBottom: '.5em',
    marginLeft: '.5em',
    marginRight: '.5em',
    borderRadius: '2px',
  },
  isBoth: {
    marginTop: '1em',
    marginBottom: '1em',
    marginLeft: '1em',
    marginRight: '1em',
    borderRadius: '2px',
  },
  editorContainer: {
    minHeight: '50vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
}

class BroadcastItem extends React.Component {
  constructor(props) {
    super(props)

    this.renderNormalCell = this.renderNormalCell.bind(this)
    this.renderEditor = this.renderEditor.bind(this)

    this.setState({
      expandedIdx: this.props.expandedIdx,
    })
  }

  renderNormalCell() {
    const { broadcast } = this.props
    const { name, status } = broadcast

    return (<div>
      <CardHeader
        title={name}
        subtitle={status}
      />
      <CardActions>
        <span>
          { Moment.unix(broadcast.scheduledTime).format('ll') }
        </span>
        <FlatButton
          onClick={() => this.props.handleEdit(broadcast)}
          label="Edit"
        />
        <FlatButton
          onClick={this.props.handleDelete}
          label="Delete"
        />
        <FlatButton
          onClick={this.props.handleSend}
          label="Send Now"
        />
      </CardActions>
    </div>)
  }

  renderEditor() {
    return (
      <div style={styles.editorContainer}>
        editor placeholder
      </div>
    )
  }

  render() {
    const {
      broadcast,
      idx,
      lastIdx,
      expandedIdx,
    } = this.props

    const isFirst = idx === 0
    const isLast = idx === lastIdx
    const expanded = idx === expandedIdx
    const isPrev = idx === expandedIdx - 1
    const isNext = idx === expandedIdx + 1

    const paperStyle = {
      ...styles.paper,
      ...isNext && styles.isFirst,
      ...isPrev && styles.isLast,
      ...isLast && styles.isLast,
      ...isFirst && styles.isFirst,
      ...((isFirst && isPrev) || (isLast && isNext)) && styles.isBoth,
      ...expanded && styles.isExpanded,
    }

    if (broadcast.id === 1) {
      console.log(
        'broadcast', broadcast,
        '\n isFirst:', isFirst,
        '\n isLast:', isLast,
        '\n expanded:', expanded,
        '\n isPrev:', isPrev,
        '\n isNext:', isNext,
        paperStyle
      )
    }

    const containerStyle = {
      ...styles.container,
      ...expanded && { overflow: 'visible' },
    }

    return (<div
      style={containerStyle}
    >
      <Paper
        style={paperStyle}
        zDepth={expanded ? 3 : 1}
      >
        {
          expanded ? this.renderEditor() : this.renderNormalCell()
        }
        {
          isLast || isPrev || expanded ? null : <Divider />
        }
      </Paper>
    </div>)
  }
}

BroadcastItem.propTypes = {
  handleEdit: React.PropTypes.func,
  handleDelete: React.PropTypes.func,
  handleSend: React.PropTypes.func,
  broadcast: React.PropTypes.shape({
    name: React.PropTypes.string,
    status: React.PropTypes.string,
    scheduledTime: React.PropTypes.number,
  }),
  idx: React.PropTypes.number,
  lastIdx: React.PropTypes.number,
  expandedIdx: React.PropTypes.number,
}

export default BroadcastItem
