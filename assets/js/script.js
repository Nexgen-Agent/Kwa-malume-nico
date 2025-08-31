const { error } = require("console");

function sendMail(){
    const templatesparams ={
        name: document.querySelector("#name").velue,
        email: document.querySelector("#email").velue,
        subject: document.querySelector("#subject").velue,
        message: document.querySelector("#message").velue,
    
    };
    emailjs.send("service_pdwcuat", "template_rq0e43j", templatesparams)
    .then(()=>{
        alert("Email sent successfully");
    })
    .catch((error)=>{
        console.log("Error sending email:", error);
        alert("failed to send email. please try again.");
    });
}