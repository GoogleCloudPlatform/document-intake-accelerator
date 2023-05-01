SELECT __patientName as Name,
       __patientPhone as Phone,
       __patientDoB as DoB,
       __clinicalReasonForUrgency as clinicalReasonForUrgency,
    __rpName as rpName,
       __rpSpecialty as rpSpecialty,
       __spSpecialty as spSpecialty
       FROM `.validation.pa_forms_texas_flat`
