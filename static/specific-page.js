// Used to trigger the FORM of review
window.onload = function() {
    stars = document.querySelectorAll(".ratings span")
    products = document.querySelectorAll(".ratings")
    ratings_list = []; 
    ratings(stars, ratings_list)
    fetch(products)
    console.log(ratings_list)
}


function TriggerReview() {
    review_gadgets = document.querySelectorAll(".review_staff")
    // console.log(review_gadgets)
    for(let review_gadget of review_gadgets){
        review_gadget.setAttribute("style", "display: block;")
    }
}

function HideReview() {
    review_gadgets = document.querySelectorAll(".review_staff")
    // console.log(review_gadgets)
    for(let review_gadget of review_gadgets){
        review_gadget.setAttribute("style", "display: none;")
    }
}

//ratings system
// A long way to go......
function ratings(stars, ratings_list){
    ////test
    // console.log(stars)
    // console.log(products)

    for(let star of stars){
        star.addEventListener("click", function(){
            // User can only rate one time
            let children = star.parentElement.children
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
            ratings_list.push(data);
            localStorage.setItem("rating", JSON.stringify(ratings_list))            
        })
    }
}

function fetch(products){
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
}
