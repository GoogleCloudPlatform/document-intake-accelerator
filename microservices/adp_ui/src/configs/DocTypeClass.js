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

import "isomorphic-fetch";

let baseUrl = process.env.REACT_APP_BASE_URL;
function fetchConfig(configServer) {
    return new Promise(function(resolve, reject) {
        console.log("fetchConfig from " + configServer);

        function handleFetchErrors(response) {
            if (!response.ok) {
                let msg = "Failure when fetching Configurations";
                let details = `${msg}: ${response.url}: the server responded with a status of ${response.status} (${response.statusText})`;
                console.log(msg + ": errorClass: " + details);
                reject(msg);
            }
            return response;
        }

        resolve (fetch(configServer + "/config_service/v1/get_config?name=document_types_config").then(handleFetchErrors).then(r => r.json())
            .then(documentConfig => {
                console.log("documentConfig", documentConfig);
                let data = documentConfig['data']
                var docs = []
                console.log("data", data);
                for(var key in data) {
                    var docObj = {}
                    docObj['value'] = key
                    docObj['display_name'] = data[key]['display_name']
                    docs[ key ] = docObj
                    docs.push(docObj)

                console.log("docs", docs)
                }

                return docs;

            })
            .catch(err => {
                console.log("error doing fetch():" + err);
                reject(err);
            }));
    });
}

const sorting = fetchConfig(baseUrl);


export default sorting