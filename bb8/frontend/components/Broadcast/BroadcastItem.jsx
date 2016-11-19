import React from 'react'
import Moment from 'moment'
import FlatButton from 'material-ui/FlatButton'
import Divider from 'material-ui/Divider'
import Paper from 'material-ui/Paper'
import {
  Card,
  CardActions,
  CardHeader,
} from 'material-ui/Card'
import Toggle from 'material-ui/Toggle'

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
    overflow: 'hidden',
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
    justifyContent: 'left',
    padding: '1.5em',
  },
  infoHeader: {
    display: 'flex',
  },
  infoHeaderTextStyle: {
    flex: 1,
  },
  infoHeaderGroupRight: {
    fontSize: '.875em',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
  },
  infoHeaderToggle: {
    flex: 'none',
    width: 'auto',
    padding: '0 1em',
  },
  infoHeaderToggleLabel: {
  },
  infoActionsContainer: {
    display: 'flex',
    marginTop: '1em',
  },
  infoActionsGroup: {
    flex: 1,
  },
}

class BroadcastItem extends React.Component {
  constructor(props) {
    super(props)

    this.renderCell = this.renderCell.bind(this)
  }

  renderCell() {
    const { broadcast } = this.props
    const { name, status, scheduledTime } = broadcast

    return (<Card
      style={styles.infoContainer}
    >
      <CardHeader
        title={name}
        subtitle={status}
        style={styles.infoHeader}
        textStyle={styles.infoHeaderTextStyle}
      >
        <div style={styles.infoHeaderGroupRight}>
          <Toggle
            label={true ? 'Scheduled' : 'Set schedule'}
            defaultToggled
            style={styles.infoHeaderToggle}
            labelStyle={styles.infoHeaderToggleLabel}
          />
          <FlatButton
            style={{ display: 'flex', alignItems: 'center' }}
            labelStyle={{
              textTransform: 'none',
            }}
            label={
              Moment.unix(scheduledTime).calendar(null, {
                sameElse: 'll',
              })
            }
            labelPosition="before"
          />
        </div>
      </CardHeader>
      <CardActions style={styles.infoActionsContainer}>
        <div style={styles.infoActionsGroup}>
          <FlatButton
            onClick={() => this.props.handleEdit(broadcast)}
            label="edit"
          />
          <FlatButton
            onClick={this.props.handleDelete}
            label="discard"
            secondary
          />
        </div>
        <div style={{ ...styles.infoActionsGroup, ...{ flex: 'none' } }}>
          <FlatButton
            onClick={this.props.handleSend}
            label="Send Now"
            primary
          />
        </div>
      </CardActions>
    </Card>)
  }

  render() {
    const {
      isFirst,
      isLast,
      expanded,
      isPrev,
      isNext,
    } = this.props

    const paperStyle = {
      ...styles.paper,
      ...isNext && styles.isFirst,
      ...isPrev && styles.isLast,
      ...isLast && styles.isLast,
      ...isFirst && styles.isFirst,
      ...((isFirst && isPrev) || (isLast && isNext)) && styles.isBoth,
      ...expanded && styles.isExpanded,
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
          expanded ? (
            <BroadcastEditor
              handleCloseEditor={this.props.handleCloseEditor}
              styles={styles}
              broadcast={this.props.broadcast}
            />
          ) :
            this.renderCell()
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
  handleCloseEditor: React.PropTypes.func,
  handleDelete: React.PropTypes.func,
  handleSend: React.PropTypes.func,
  broadcast: React.PropTypes.shape({
    // eslint-disable-next-line react/no-unused-prop-types
    name: React.PropTypes.string,
    // eslint-disable-next-line react/no-unused-prop-types
    status: React.PropTypes.string,
    // eslint-disable-next-line react/no-unused-prop-types
    scheduledTime: React.PropTypes.number,
  }),
  isFirst: React.PropTypes.bool,
  isLast: React.PropTypes.bool,
  expanded: React.PropTypes.bool,
  isPrev: React.PropTypes.bool,
  isNext: React.PropTypes.bool,
}

export default BroadcastItem
