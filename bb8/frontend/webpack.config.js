const path = require('path')
const webpack = require('webpack')
const ExtractTextPlugin = require('extract-text-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')

const isDebug = global.DEBUG === false ? false : !process.argv.includes('--release')
const isVerbose = process.argv.includes('--verbose') || process.argv.includes('-v')

const defaultConfig = {
  context: __dirname,
  devServer: {
    port: '8080',
    contentBase: './build',
    inline: true,
    proxy: {
      '/': {
        target: 'https://localhost:' + process.env.HTTP_PORT,
        secure: false
      }
    },
  },
  entry: {
    app: './index',
  },
  output: {
    path: path.resolve(__dirname, './dist'),
    publicPath: '/',
    filename: '[name].[hash].js',
  },
  debug: isDebug,
  resolve: {
    extensions: ['', '.js', '.jsx']
  },
  module: {
    preLoaders: [
        { test: /\.jsx?$/, loader: 'eslint', exclude: /node_modules/ },
    ],
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: [/node_modules/],
        loader: 'babel',
        query: {
          presets: ['es2015', 'react'],
          plugins: ["transform-class-properties"],
        },
      },
      {
        test: /\.(eot|svg|png)$/,
        loader: 'url-loader?limit=200000',
      },
      {
        test: /\.scss$/,
        loader: ExtractTextPlugin.extract(['css-loader', 'sass-loader'])
      },
      {
        test: /.*\.html$/,
        loader: 'file?name=[name].[ext]',
      },
    ],
  },
  postcss: [
    require('autoprefixer')(),
  ],
  plugins: [
    new webpack.DefinePlugin({
          'process.env.BB8_DEPLOY': process.env.BB8_DEPLOY,
          'process.env.HTTP_PORT': process.env.HTTP_PORT,
    }),
    new HtmlWebpackPlugin({
      inject: false,
      title: 'Compose.ai',
      template: require('html-webpack-template'),
      appMountId: 'root',
      meta: {
        description: 'Compose.ai website'
      },
      mobile: true,
      links: [
        'https://fonts.googleapis.com/css?family=Roboto',
      ],
    }),
    new ExtractTextPlugin('[name].[hash].css'),
  ],
}

module.exports = defaultConfig
