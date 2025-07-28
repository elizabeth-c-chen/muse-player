
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

// // IN PROGRESS
// function setLovedStatus(event, songId) {
//     const result = client.db("museplayer").collection("songs").findOne( {"_id": songId});
//     const lovedStatus = result.isFavorited;
//     if (lovedStatus == 0) {
//         client.db("museplayer").collection("songs").updateOne(
//             {_id: songId}, 
//             {$set: {isFavorited: 1}}
//         );
//         const lovedTextIcon = document.getElementsByClassName("loved-icon").innerHTML;
//         lovedTexticon = lovedTextIcon.replace("♡", "♥");
//         document.getElementById("loved-icon").innerHTML = lovedTextIcon;

//     } else {
//         client.db("museplayer").collection("songs").updateOne(
//             {_id: songId}, 
//             {$set: {isFavorited: 0}}
//         );
//         const lovedTextIcon = document.getElementById("loved-icon").innerHTML;
//         lovedTexticon = lovedTextIcon.replace("♥", "♡");
//         document.getElementById("loved-icon").innerHTML = lovedTextIcon;
//     }





//     var timer;
//     var percent = 0;
//     var audio = document.getElementById("audio");
//     audio.addEventListener("playing", function(_event) {
//       var duration = _event.target.duration;
//       advance(duration, audio);
//     });
//     audio.addEventListener("pause", function(_event) {
//       clearTimeout(timer);
//     });
//     var advance = function(duration, element) {
//       var progress = document.getElementById("progress");
//       increment = 10/duration
//       percent = Math.min(increment * element.currentTime * 10, 100);
//       progress.style.width = percent+'%'
//       startTimer(duration, element);
//     }
//     var startTimer = function(duration, element){ 
//       if(percent < 100) {
//         timer = setTimeout(function (){advance(duration, element)}, 100);
//       }
//     }
    
//     function togglePlay (e) {
//       e = e || window.event;
//       var btn = e.target;
//       if (!audio.paused) {
//         btn.classList.remove('active');
//         audio.pause();
//         isPlaying = false;
//       } else {
//         btn.classList.add('active');
//         audio.play();
//         isPlaying = true;
//       }
//     }
    
    
    
//     .each(function(){
//       var x = $(this).css("height");
//       var text = $(this).children('.v_text');
//       text.css({"transform":"translateX("+x+") rotate(-90deg)", "width":x});
//     });