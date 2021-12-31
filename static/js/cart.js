var updateBtns = document.getElementsByClassName('update-cart') 
//variabila momoreaza toate butoanele cu clasa update-cart 
//(cele de adaugat in cos de la fiecare produs si cele din cart de schimbat cantitatea)

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'Action:', action)

        console.log('USER:', user)
        if(user == 'AnonymousUser') {
            console.log('User-ul nu este autentificat')
        }else{
            updateUserOrder(productId, action) ///doar daca e logat userul se poate face update la items 
        }
    })
}


function updateUserOrder (productId, action){
    console.log('Userul este logat, se trimit date..')

    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers:{
            'Content-Type' : 'application/json',
            'X-CSRFToken' : csrftoken,
        },
        //body - datele pe care le trimitem la backend
        //folodim JSON - JavaScript Object Notation
        //se foloseste pt transferul datelor de pe server la pagina web sau invers
        body:JSON.stringify({'productId': productId,  'action':action})

    })

    .then((response) => {
        return response.json()
    })

    .then((data) => {
        console.log('data:', data)
        setTimeout(function(){  //se face reload-ul paginii dupa ce se updateaza un item 
            window.location.reload();
        },100); 
    });
}