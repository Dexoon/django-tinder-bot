const path = require("path");
const BundleTracker = require("webpack-bundle-tracker");
const {CleanWebpackPlugin} = require("clean-webpack-plugin");

module.exports = {
    entry: {
        tinder: "./src/tinder/index.js",
        chats: "./src/chats/index.js",
    },
    output: {
        path: path.resolve("static/"),
        publicPath: '/static/',
        filename: "[name]-[fullhash].js",
    },
    plugins: [
        new CleanWebpackPlugin(),
        new BundleTracker({
            path: __dirname,
            filename: "./webpack-stats.json",
        }),

    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: ["babel-loader"],
            },
            {
                test: /\.css$/,
                use: ["style-loader", "css-loader"],
            },
        ],
    },
};
