
// "use strict";

// const { MongoClient } = require("mongodb");
// // Connection URI
// const uri = "mongodb://127.0.0.1:27017/";
// // Create a new MongoClient
// const client = new MongoClient(uri);

// // async function run() {
// //   try {
// //     // Connect the client to the server
// //     await client.connect();
// //     // Establish and verify connection
// //     await client.db("admin").command({ ping: 1 });
// //     console.log("Connected successfully to MongoBB");
// //   } finally {
// //     // Ensures that the client will close when you finish/error
// //     await client.close();
// //   }
// // }
// // run().catch(console.dir);



// // const playOrPause = function(){
// //     $.post("/play").done(function(){});
// //     return
// // };

// // const post = (endpoint) => fetch(endpoint, { method: "POST" });


// // const playOrPause = () => {
// //   post("/play")
// //     .then(response => response.text())
// //     .then(result => {
// //       console.log("Playback toggled:", result);
// //       // Optionally update UI here
// //     });
// // };

// // const rewind = () => post("/rewind");

// // const fastForward = () => post("/fast-forward");

// // const shuffle = () => post("/shuffle");


// // function changeRepeatMode() {
// //     fetch("/change-repeat", { method: "POST" })
// //         .then(response => response.json())
// //         .then(data => {
// //             const mode = data.new_mode;  // e.g. "repeat_all"
// //             const repeatIcon = document.getElementById("repeat-icon");

// //             const iconMap = {
// //                 "repeat_none": "/static/icons/controls/repeat-off.png",
// //                 "repeat_all": "/static/icons/controls/repeat-all.png",
// //                 "repeat_one": "/static/icons/controls/repeat-one-on.png"
// //             };

// //             repeatIcon.src = iconMap[mode];
// //         })
// //         .catch(error => {
// //             console.error("Error updating repeat mode:", error);
// //         });
// // }


// // document.addEventListener("DOMContentLoaded", () => {
// //   const repeatIcon = document.getElementById("repeat-icon");
// //   const mode = "{{ repeat_mode }}";
// //   const iconMap = {
// //     "repeat_none": "/static/icons/controls/repeat-off.png",
// //     "repeat_all": "/static/icons/controls/repeat-all.png",
// //     "repeat_one": "/static/icons/controls/repeat-one-on.png"
// //   };
// //   if (repeatIcon && mode in iconMap) {
// //     repeatIcon.src = iconMap[mode];
// //   }
// // });


