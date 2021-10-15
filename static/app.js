const apiUrl = ''
const container = document.getElementById("app");

function getCookie(name) {
    return document.cookie.replace(
        new RegExp(`(?:(?:^|.*;\\s*)${name}\\s*=\\s*([^;]*).*$)|^.*$`),
        "$1"
    );
}
const token = getCookie('Token')
const user_objectId = getCookie('_id')
const user_tsmcid = getCookie('id')
// console.log('cookie:', document.cookie)
// console.log('token:', token)
// console.log('user_objectId:', user_objectId)
// console.log('user_tsmcid:', user_tsmcid)

const myorders = document.getElementById('myorders')
const search_input = document.getElementById('search_bar')
const logoutButton = document.getElementById('logout')
const toggle_bar = document.getElementById('toggle_bar')
const loginButton = document.getElementById('user_id')

loginButton.innerText = user_tsmcid

function onclickToggleBarButton(button, routeName) {
    // update button color
    toggle_bar.childNodes.forEach(e => {
        try {
            e.classList.remove('accent_color')
        } catch { }
    })
    button.classList.add('accent_color')

    fetchOrders(routeName)
}

const loggedIn = (token != '')
function animateHidden(e, hidden) {
    e.style.height = hidden ? 0 : e.scrollHeight + 'px'
}
animateHidden(document.getElementById('login').parentNode, loggedIn)
animateHidden(myorders.parentNode, !loggedIn)
animateHidden(logoutButton.parentNode, !loggedIn)

const nextTheme = loggedIn ? {
    light2: 'light',
    light: 'default',
    default: 'dark',
    dark: 'light2'
} : {
    default: 'dark',
    light: 'dark',
    light2: 'dark',
    dark: 'light2'
}
var theme // may be null, 'light', 'light2', 'dark', 'default'
function onClickChangeTheme(button) {
    document.body.classList.remove(theme)
    theme = nextTheme[theme] || 'light2'
    document.body.classList.add(theme)
    localStorage.setItem('theme', theme)
}

function removeCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}
function logout() {
    removeCookie('Token');
    removeCookie('_id');
    removeCookie('id');

    // redirect to main page
    window.location.replace('/')
}
logoutButton.onclick = logout

// Post JSON template
// 
// function postJSON(url, data) {
//     // Default options are marked with *
//     return fetch(url, {
//         body: JSON.stringify(data), // must match 'Content-Type' header
//         cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
//         credentials: 'same-origin', // include, same-origin, *omit
//         headers: {
//             'user-agent': 'Mozilla/4.0 MDN Example',
//             'content-type': 'application/json'
//         },
//         method: 'POST', // *GET, POST, PUT, DELETE, etc.
//         mode: 'no-cors', // no-cors, cors, *same-origin
//         redirect: 'follow', // manual, *follow, error
//         referrer: 'no-referrer', // *client, no-referrer
//     })
//         .then(response => response.json()) // 輸出成 json
// }

// update join button UI & make join/unjoin requests
function onClickJoinButton(joinButton, orderId) {
    if (joinButton.classList.contains('joined')) { // quit order
        joinButton.disabled = true
        joinButton.innerHTML = 'unjoining...'

        fetch(apiUrl + `/Order/QuitOrder/${user_objectId}/${orderId}`, {
            headers: {
                'x-access-token': token
            },
            mode: 'cors', // no-cors, cors, *same-origin
            method: 'POST'
        })
            .then(res => res.json())
            .then(json => {
                var message = json.message
                switch (message) {
                    case "This order is already closed, you couldn't quit":
                        message = "Couldn't quit"
                        break;
                    case 'Remove Success!':
                        message = 'Join'
                        joinButton.classList.remove('joined')
                }
                joinButton.innerText = message
            })
            .catch(err => {
                joinButton.classList.add('err')
                joinButton.innerText = 'Our fault'
            }).finally(() => {
                joinButton.disabled = false
            })
    } else { // join order
        joinButton.disabled = true
        joinButton.innerHTML = 'joining...'

        fetch(apiUrl + `/Order/JoinOrder/${user_objectId}/${orderId}`, {
            headers: {
                'x-access-token': token
            },
            mode: 'cors', // no-cors, cors, *same-origin
            method: 'POST'
        })
            .then(res => res.json())
            .then(json => {
                var buttonText = json.message
                switch (buttonText) {
                    case 'The number is full':
                        buttonText = 'Full'
                        break;
                    case 'you are already in this order':
                        buttonText = 'Already joined'
                        break;
                    case 'success':
                        // successfully joined
                        buttonText = 'Joined'
                        // joinButton.title = "Click to cancel"
                        joinButton.classList.add('joined')
                }
                joinButton.innerText = buttonText
            })
            .catch(err => {
                joinButton.classList.add('err')
                joinButton.innerText = 'Our fault'
            }).finally(() => {
                joinButton.disabled = false
            })
    }
}

function onClickHashTag(tag) {
    const str = tag.text.slice(1) // '#hashtag' -> 'hashtag'
    search_input.value = str
    searchByHashTag(str)
}

// convert a Date object to e.g. '9:00'
function getTime(date) {
    return `${date.getHours()}:${('0' + date.getMinutes()).slice(-2)}`
}

// convert a Date object to e.g. '7/21'
function getDate(date) {
    return `${date.getMonth() + 1}/${date.getDate()}`
}

// after you get the 'orders' data,
// use this function to display them.
function showOrders(orders) {
    if (orders.length) {
        var s = ''
        orders.forEach(order => {
            var order_closed = order.status == 'CLOSED'

            // make join button
            var joinButton = ''
            if (loggedIn && !order_closed) {
                if (order.creator_id != user_tsmcid) {
                    var joined = false
                    try {
                        for (let i = 0; i < order.join_people_id.length; i++) {
                            const e = order.join_people_id[i];
                            if (e == user_tsmcid) {
                                joined = true
                                break
                            }
                        }
                    } catch (error) { }
                    if (joined) {
                        joinButton = `<button class="round_bar_button joined" onclick="onClickJoinButton(this, '${order._id}')">Joined</button>`
                    } else {
                        if (order.join_people < order.join_people_bound) {
                            joinButton = `<button class="round_bar_button" onclick="onClickJoinButton(this, '${order._id}')">Join</button>`
                        } else {
                            joinButton = `<button class="round_bar_button" onclick="onClickJoinButton(this, '${order._id}')">Full</button>`
                        }
                    }
                } else {
                    joinButton = `<p>My Order</p>`
                }
            }

            // make meet time
            var meet_time_start = new Date(order.meet_time[0])
            var meet_time_end = new Date(order.meet_time[1])
            var meet_time
            if (meet_time_start.toLocaleDateString() == meet_time_end.toLocaleDateString()) {
                meet_time = `
                <p class="lightgraytext">
                    <span class="short_date">${getDate(meet_time_start)}</span><br>
                    ${getTime(meet_time_start)} - ${getTime(meet_time_end)}
                </p>
            `;
            } else {
                meet_time = `
                <p class="lightgraytext">
                    ${meet_time_start.toLocaleString().slice(0, -3)} - ${meet_time_end.toLocaleString().slice(0, -3)}
                </p>
            `;
            }

            // make hashtags
            var hashtags = ''
            order.hashtag.forEach(hashtag => {
                hashtags += `<a class="hashtag hover_opacity" onclick="onClickHashTag(this)">#${hashtag}</a> `
            })

            // fix factory text.  E.g. 14P7 -> FAB14P7
            var meet_factory = order.meet_factory
            try {
                if (!isNaN(meet_factory[0]))
                    meet_factory = 'FAB' + meet_factory
            } catch (error) { }

            // order status indicator.  E.g. '3/5', 'Closed'
            var order_status
            if (order_closed) {
                order_status = `<span title="Joined: ${order.join_people_id}">Closed</span>`
            } else {
                order_status = `<span title="Joined: ${order.join_people_id?.join(', ')}. 還差 ${order.join_people_bound - order.join_people} 人">${order.join_people}/${order.join_people_bound}</span>`
            }

            s += `
                <div class="card ${loggedIn ? 'loggedIn' : ''} ${order.epidemic_prevention_group}">
                    <span class="card--group">${order.epidemic_prevention_group}</span>
                    <div class="invisible_scroll">
                        <h1 class="card--title">${order.drink} ${order.title}</h1>
                        <p class="card--comment">${order.comment}</p>
                        <p class="card--creator_id" title="Creator">${order.creator_id}, ${order_status}</p>
                    </div>
                    <div class="absoluteBottom">
                        ${meet_time}
                        <div class="invisible_scroll hashtag_panel_height">
                            <p class="card--fab">${order.store}, ${meet_factory}</p>
                            <p>${hashtags}</p>
                        </div>
                        ${joinButton}
                    </div>
                </div>
            `;
        });
    } else {
        // s = '<p>Nothing to show</p>'
        s = `<div><button class="round_bar_button no_result">No result</button><div>`
    }
    container.innerHTML = s
    container.style.opacity = 1 // fadein cards
}


var searchStr = ''
function searchByHashTag(str) {
    // console.log('searchBar_onKeyUp()')
    // console.log(e)
    str = str.trim()
    if (str === searchStr)
        return
    searchStr = str

    if (str == '') {
        fetchOrders()
        return
    }

    container.style.opacity = 0
    fetch(apiUrl + '/Order/SearchByHashtag', {
        method: 'POST',
        mode: 'cors', // no-cors, cors, *same-origin
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ search_key: str }),
    })
        .then(response => response.json())
        .then(data => showOrders(data));
    // .catch(error => {})
}

// fetch & show orders
function fetchOrders(route = 'ListAllInProgressGroupOrder') {
    container.style.opacity = 0
    fetch(apiUrl + '/Order/' + route, {
        mode: 'cors',
    })
        .then(response => response.json())
        .then(data => showOrders(data));
}

fetchOrders()

if (localStorage.getItem('theme') === null) { // if user haven't tried other theme
    const button_change_theme = document.getElementById('button_change_theme')
    // intent user to try out dark theme
    setTimeout(() => {
        button_change_theme.classList.add('hightlight')
        setTimeout(() => {
            button_change_theme.classList.remove('hightlight')
        }, 5000);
    }, 1000);
}
