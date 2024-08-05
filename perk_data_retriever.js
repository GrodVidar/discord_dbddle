var perks = document.querySelectorAll('tr._1e4q60a');

var perk_data = {}

for(var i = 0; i < perks.length; i++) {
    var perk_name = perks[i].children[0].children[1].children[0].text;
    var perk_popularity = perks[i].children[1].children[0].children[1].children[0].innerHTML;
    perk_data[perk_name] = parseFloat(perk_popularity)

}