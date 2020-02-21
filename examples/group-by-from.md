Possibly you need modify labels:

```
labels: { $in: ['inbox'] }
```

You can see all your labels in [group-by-labels](https://github.com/Rpsl/mongodb-gmail/blob/master/examples/group-by-labels.md)

```
db.mails.aggregate([
    { $match: { labels: { $in: ['inbox'] } } },
    { $group: {_id: "$from", total: {$sum : 1} } },
    { $sort : {"total": -1 } }

```
