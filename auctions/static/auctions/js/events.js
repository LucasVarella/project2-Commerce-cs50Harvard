
function listAuction(id){
    window.location.href= `auctions/${id}`
}

addEventListener('DOMContentLoaded', function(){
    
    var auctions = document.querySelectorAll('.button-bid');
    var auctions_array = [...auctions];
    auctions_array.forEach(auction => {
        auction.onclick = function(){
            id = auction.dataset.auction_id;
            listAuction(id);
        };
    });  
    
});






