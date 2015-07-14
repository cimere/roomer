> db.rooms.find({"name": "INNOVATION 360"}, {"_id": 1})
{ "_id" : ObjectId("52666ee67e165bc6739b597c") }
> db.rooms.find({"name": "TRUST"}, {"_id": 1})
{ "_id" : ObjectId("52666ee67e165bc6739b597a") }
> db.rooms.find({"name": "INITIATIVE"}, {"_id": 1})
{ "_id" : ObjectId("52666ee67e165bc6739b5979") }
> db.rooms.find({"name": "CUSTOMER FIRST"}, {"_id": 1})
{ "_id" : ObjectId("52666ee67e165bc6739b597b") }

> db.groups.find().pretty()
{
    "_id" : ObjectId("546084a8184542150f68fc6d"),
    "name" : "Engineer",
    "rooms" : [
        "52666ee67e165bc6739b597c",
        "52666ee67e165bc6739b597a",
        "52666ee67e165bc6739b5979",
        "52666ee67e165bc6739b597b"
    ]
}
{
    "_id" : ObjectId("546084c2184542150f68fc6e"),
    "name" : "Operations",
    "rooms" : ["5460b82b184542150f68fc70"]
}

db.users.find({},{tags:true}).forEach(function(v){ db.users.update({ _id: v["_id"]}, { $set: { "groups": ["546084a8184542150f68fc6d"] } } )});


db.rooms.insert({
    "desc" : "Aperta, fino a 8 persone.",
    "name" : "STANZA 1",
    "people" : 8,
    "reservations" : [],
    "tel" : null,
    "type" : "chiusa",
    "vdc" : null,
    "whiteboard" : "muro lavagna"
})
db.rooms.insert({
    "desc" : "Aperta, fino a 8 persone.",
    "name" : "STANZA 2",
    "people" : 8,
    "reservations" : [],
    "tel" : null,
    "type" : "chiusa",
    "vdc" : null,
    "whiteboard" : "muro lavagna"
})
db.rooms.insert({
    "desc" : "Aperta, fino a 8 persone.",
    "name" : "STANZA 3",
    "people" : 8,
    "reservations" : [],
    "tel" : null,
    "type" : "chiusa",
    "vdc" : null,
    "whiteboard" : "muro lavagna"
})
db.rooms.insert({
    "desc" : "Aperta, fino a 8 persone.",
    "name" : "STANZA 4",
    "people" : 8,
    "reservations" : [],
    "tel" : null,
    "type" : "chiusa",
    "vdc" : null,
    "whiteboard" : "muro lavagna"
})
db.rooms.insert({
    "desc" : "Aperta, fino a 8 persone.",
    "name" : "STANZA 5",
    "people" : 8,
    "reservations" : [],
    "tel" : null,
    "type" : "chiusa",
    "vdc" : null,
    "whiteboard" : "muro lavagna"
})

db.users.insert({"_id" : "aceri", "firstname" : "Alessandro", "lastname" : "Ceri", "email" : "alessandro.ceri@fastweb.it", "groups" : ["546084c2184542150f68fc6e"]})
