/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

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