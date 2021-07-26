
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

// IN PROGRESS
function setLovedStatus(event, songId) {
    const result = client.db("museplayer").collection("songs").findOne( {"_id": songId});
    const lovedStatus = result.isFavorited;
    if (lovedStatus == 0) {
        client.db("museplayer").collection("songs").updateOne(
            {_id: songId}, 
            {$set: {isFavorited: 1}}
        );
        const lovedTextIcon = document.getElementsByClassName("loved-icon").innerHTML;
        lovedTexticon = lovedTextIcon.replace("♡", "♥");
        document.getElementById("loved-icon").innerHTML = lovedTextIcon;

    } else {
        client.db("museplayer").collection("songs").updateOne(
            {_id: songId}, 
            {$set: {isFavorited: 0}}
        );
        const lovedTextIcon = document.getElementById("loved-icon").innerHTML;
        lovedTexticon = lovedTextIcon.replace("♥", "♡");
        document.getElementById("loved-icon").innerHTML = lovedTextIcon;
    }
        


$(document).ready(() => {
});

