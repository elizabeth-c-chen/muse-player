
"use strict";

const { MongoClient } = require("mongodb");
// Connection URI
const uri = "mongodb://127.0.0.1:27017/";
// Create a new MongoClient
const client = new MongoClient(uri);

async function run() {
  try {
    // Connect the client to the server
    await client.connect();
    // Establish and verify connection
    await client.db("admin").command({ ping: 1 });
    console.log("Connected successfully to MongoBB");
  } finally {
    // Ensures that the client will close when you finish/error
    await client.close();
  }
}
run().catch(console.dir);

const playOrPause = function(){
    $.post("/play").done(function(){});
    return
};
const rewind = function(){
    $.post("/rewind").done(function(){});
    return
};

const fastForward = function(){
    $.post("/fast-forward").done(function(){});
    return
};

const shuffle = function(){
    $.post("/shuffle").done(function(){});
    return
};

const changeRepeatMode = function(){
    $.post("/change-repeat").done(function(){});
    return
};


