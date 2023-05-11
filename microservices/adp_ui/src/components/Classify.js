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

import React, { useState, useEffect, useRef } from 'react';
import { Container, Col, Row, Button, FloatingLabel, Form, Card, ProgressBar } from 'react-bootstrap';

import { useHistory } from 'react-router-dom'
import {
  useLocation, Link, useParams
} from "react-router-dom";
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import { BsFillCheckCircleFill } from 'react-icons/bs';
import 'react-toastify/dist/ReactToastify.css';
import { baseURL } from '../configs/firebase.config';
import options from '../configs/DocTypeClass';
import { ReactComponent as Check } from '../images/check-circle.svg';
import { ReactComponent as File } from '../images/file.svg';
import { ReactComponent as Cross } from '../images/cancel.svg';
import Headers from './Headers';
import { ReactComponent as Back } from '../images/arrow-back.svg';
import '../App.css'
import '../css/DocumentReview.css'

var pdfjsLib = window['pdfjs-dist/build/pdf'];
pdfjsLib.GlobalWorkerOptions.workerSrc = '//mozilla.github.io/pdf.js/build/pdf.worker.js';

let inputData = [];
let viewer = '';
let dropDown = '';
var context = '';
let canvas = '';
var thePdf = null;
let optionsSorted = [];

function  Classified() {
  const { uid, caseid } = useParams();
  const [notes, setNotes] = useState('');
  const [docType, setDocType] = useState('');
  const history = useHistory();

  useEffect(() => {
    // based on the uid, get the document for the page
    let url = `${baseURL}/hitl_service/v1/fetch_file?case_id=${caseid}&uid=${uid}`
    optionsSorted = options.then((res) => {
      optionsSorted=res;
      dropDown = document.getElementById('dropdown-basic-button');
      res.forEach(item => {
          dropDown.appendChild(new Option(item["display_name"] , item["value"]));
          console.log("drop-down:", item["display_name"], item["value"])
      })
      console.log("optionsSorted", optionsSorted)
    });


    axios.post(`${baseURL}/hitl_service/v1/get_document?uid=${uid}`, {
    }).then(res => {
      console.log("API RESPONSE DATA", res.data);
      inputData = res.data.data;

      // To display PDF onload
      pdfjsLib.getDocument(url).promise.then(function (pdf) {
        thePdf = pdf;
        viewer = document.getElementById('pdf-viewer');
        renderPage(pdf.numPages)
      });

    }).catch((err) => {
      console.log("error", err);
      toast.error(`${err}`, {
        position: "bottom-center",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  let currPage = 1;

  // Based on the pagenumbers the PDF can be rendered
  function renderPage() {
    //pageNumber = 1;
    thePdf.getPage(currPage).then(function (page) {
      console.log('Page loaded');
      canvas = document.createElement("canvas");
      canvas.className = `pdf-page-canvas-${currPage}`;
      canvas.strokeStyle = 'black'
      viewer.appendChild(canvas);
      var scale = 1.5;
      var rotation = 0;
      var dontFlip = 0;
      var viewport = page.getViewport({ scale, rotation, dontFlip });

      // Prepare canvas using PDF page dimensions
      context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      //page.render({canvasContext: canvas.getContext('2d'), viewport: viewport});
      var renderContext = {
        canvasContext: context,
        viewport: viewport
      };
      var renderTask = page.render(renderContext);
      renderTask.promise.then(function () {
        console.log("Page rendered")
      });

      currPage++;
      if (thePdf !== null && currPage <= thePdf.numPages) {
        console.log("currpage")

        thePdf.getPage(currPage).then(renderPage);
      }
    })
  }

  // This is the checkpoint to know if the document needs the manual classification or not
  const docTypeChange = (e) => {
    console.log("doc type changed", e.target.value)
    setDocType(e.target.value)
  }

  // To manual classify a document
  const classifyDoc = () => {
    console.log("DOC TYPE SELECTED", docType)
    console.log("CASEID", caseid)
    console.log("uid", uid)
    axios.post(`${baseURL}/hitl_service/v1/update_hitl_classification?case_id=${caseid}&uid=${uid}&document_class=${docType}`).then((classifiedDocData) => {
      console.log("CLassified doc data", classifiedDocData)
      history.push('/');
    })
  }



  return (
    <div>
      <Headers />
      <div className="subHeaderReassign">
        <Link to={{ pathname: '/', }} className="drBack">
          <Back fill="#aaa" />
        </Link>{' '}
        <label className={["raLabels", "raSpace"].join(" ")}> Classify Document</label>
      </div>
      <Container style={{ padding: '45px' }}>
        <Card style={{ borderRadius: '1.25rem' }}>
          <Card.Body>
            <Card.Text>
              <div className="row" style={{ marginLeft: '10px', paddingTop: '0px', background: '#fff' }}>
                <div className="col-7" style={{ overflow: 'scroll', height: 'calc(100vh - 220px)' }}>
                  {/* <iframe src={`${baseURL}/hitl_service/v1/fetch_file?case_id=${caseid}&uid=${uid}`} height='500' width='800' title="pdf" /> */}
                  <div id='pdf-viewer' style={{ width: '100%', minWidth: '800px', maxWidth: '1200px', backgroundColor: '#ccc' }}></div>
                </div>

                <div className="col-5" style={{ marginTop: '33px' }}>
                  <label className="labelBold"> Choose Document Type/Class</label>
                  <select id="dropdown-basic-button" title="Choose Document Class" onChange={(e) => docTypeChange(e)} style={{ width: '100%', borderRadius: '16px' }}>
                    <option></option>
                    {/*{optionsSorted.map(({ value, doc_type, doc_class }, index) => <option key={value} value={value} >{doc_type} {'>'} {doc_class}</option>)}*/}

                  </select>
                  <br /> <br />
                  <Row>
                    <FloatingLabel controlId="floatingTextarea" label="Notes" className="mb-3">
                      <Form.Control as="textarea" value={notes} style={{ borderRadius: '12px', height: '8rem' }} onInput={e => setNotes(e.target.value)} placeholder="Leave a comment here" />
                    </FloatingLabel>
                  </Row>
                  <Button onClick={classifyDoc} style={{ float: 'right', borderRadius: '10px' }}>Classify</Button>
                </div>

              </div>
            </Card.Text>
          </Card.Body>
        </Card>
      </Container>



    </div>

  )

}

export default Classified;