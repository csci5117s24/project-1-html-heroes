// Used to trigger the FORM of review
window.onload = function() {
    stars = document.querySelectorAll(".ratings span")
    products = document.querySelectorAll(".ratings")
    ratings()
}


function TriggerReview() {
    var checkbox = document.getElementById("q4_5");
    console.log(checkbox)
    var textarea = document.getElementById("conditional_1");
    console.log(checkbox)
    textarea.style.display = checkbox.checked ? "block" : "none";
}

//ratings system
function ratings(){
    ////test
    // console.log(stars)
    // console.log(products)
    let ratings = []; //store ratings locally. I don't think the ratings has to go to the databse

    for(let star of stars){
        star.addEventListener("click", function(){

            let children = star.parentElement.children

            // User can only rate one time
            for(let child of children){
                if(child.getAttribute("data-clicked")){
                    return false
                }
            }

            // Insert "data-clicked" attribute into <span> tag. 
            // Then We leverage this in CSS.
            this.setAttribute("data-clicked", "true")

            // Get the value of star and its class name. Use them for storage
            rating = this.dataset.rating;
            productId = this.parentElement.dataset.productid;
            // console.log(rating, productId)

            let data={
                "stars": rating,
                "product-id": productId
            }

            ratings.push(data);
            
            // store rating locally
            localStorage.setItem("rating", JSON.stringify(ratings))


            
        })
    }
}

if(localStorage.getItem("rating")){
    ratings = JSON.parse(localStorage.getItem("rating"))
    for(let rating of ratings){
        for(let product of products){
            if(rating['product-id'] == product.dataset.productid){
                let reversedStars = Array.from(product.children).reverse()
                let index = parseInt(rating["stars"]) - 1;
                reversedStars[index].setAttribute("data-clicked","true")
            }
        }
    }
}