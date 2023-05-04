SELECT __patientName as Name,
       __patientPhone as Phone,
       __patientDoB as DoB,
       __clinicalReasonForUrgency as clinicalReasonForUrgency,
    __rpName as rpName,
       __rpSpecialty as rpSpecialty,
       __spSpecialty as spSpecialty
       FROM `validation.pa_forms_texas_flat`
where timestamp > cast('2023-05-02T19:00:00' as datetime)
