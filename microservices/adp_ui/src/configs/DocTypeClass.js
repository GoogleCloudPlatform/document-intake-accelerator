const docclasstype=[

{
    'value':'utility_bill',
    'doc_type':'Supporting Documents',
    'doc_class': 'Utility Bill'
},
{
    'value':'unemployment_form',
    'doc_type':'Application Form',
    'doc_class': 'Unemployment Form'
},
{
    'value':'claims_form',
    'doc_type':'Supporting Documents',
    'doc_class': 'Claims Form'
},
{
    'value':'pay_stub',
    'doc_type':'Supporting Documents',
    'doc_class': 'Pay Stub'
},
{
    'value':'driver_license',
    'doc_type':'Supporting Documents',
    'doc_class': 'Driver License'
}
]

const sorting=docclasstype.sort(function (a, b) {
    return a.doc_type.localeCompare(b.doc_type) || a.doc_class.localeCompare(b.doc_class);
});

console.log(sorting);

export default sorting;