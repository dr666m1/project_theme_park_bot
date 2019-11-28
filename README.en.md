# concept
this app enables you to enjoy theme parks such as disney resort, USJ and so on!

# prepare
before you use this app, you have to invite it to your group or talk room.

you can search this app by ID or QR code below.

ID: `@541rhynx`

QR code:

![QR code](https://user-images.githubusercontent.com/26474260/69472396-f0b41c80-0dec-11ea-8520-f0f55cb9476c.png "QRcode")

# usage
you can use the functions below.

don't forget leading `:`. (e.g.`:help`)

myapp ignores messages without `:`.

## help (`:help`)
show the link to this page.

## combination `:combination` or `:comb`
make pairs in a random manner from the member list which is passed as arguments.

see below for an example.

once you pass a list, it'll be cached.

so you don't have to pass it twice. (`:comb` or `:combination` is enough.)

the cache is associated with the group or talk room.

when you want to add some members, pass whole member list like first time.

the cache will be overwritten.

```
:comb
sato
ito
suzuki
tanaka
```

you can also pass some information for each member.

in the case below, sato and suzuki won't be paired.

```
:comb
sato male
ito female
suzuki male
tanaka female
```

## expense
### expence *integer* `:expence <int>`
record your expence.

for the second time and later, the expence is added.

### expence_split `:expence_split` or `:split`
caluculate who should pay.

you can pass the number of the members. (like `:split 4`)

in default, the number of the members who used `:expence` command is used.

### expence_clear `:expence_clear` or `:clear`
clear the record.

this affects whole members' record.

## bye `:bye`
kick out this app from the group or talk room.

when you are talkig alone, nothing will happen.
<!--
## birthday
-->

