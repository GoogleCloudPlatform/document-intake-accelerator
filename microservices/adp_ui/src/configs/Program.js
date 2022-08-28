const state=[
    {
        value:"arkansas",
        label:"Arkansas"
    },
{
    value:"arizona",
    label:"Arizona"
},

{
    value:"illinois",
    label:"Illinois"
},
{
    value:"california",
    label:"California"
}
]

const ordering = state.sort((first,second)=>first.label - second.label)
console.log("ordering",ordering)


export default ordering;