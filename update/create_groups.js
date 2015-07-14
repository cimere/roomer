use roomer
room_ids = db.rooms.find({}, {_id: 1})
rooms_ids.forEach(function(v) {
    print(v)
}
