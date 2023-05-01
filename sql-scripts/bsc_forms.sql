SELECT __beneficiaryName as Name,
       __beneficiaryAddress as Address,
       __beneficiaryState as State,
       __beneficiaryZip as Zip,
       __beneficiaryDoB as DoB,

       __procCode as procCode,
       __procDesc as procDesc,
       __spFacilityName as spFacilityName,
       __issurerName as issurerName,
       __rpSpecialty as rpSpecialty,
       __rpJustification as rpJustification
       FROM `.validation.pa_forms_bsc_flat`
