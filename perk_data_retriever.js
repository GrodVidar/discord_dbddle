var perk_data = []

for(var i = 0; i < perks.length; i++) {
    var perk_name = perks[i].children[0].children[1].children[0].text;
    var perk_popularity = perks[i].children[1].children[0].children[1].children[0].innerHTML;
    perk_data.push({"perk_name": perk_name, "perk_popularity": parseFloat(perk_popularity)})

}