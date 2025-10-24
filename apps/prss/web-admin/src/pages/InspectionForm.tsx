import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { returnsApi } from '../services/api'

export default function InspectionForm() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [finding, setFinding] = useState('ok')
  const [recommendation, setRecommendation] = useState('restock')
  const [notes, setNotes] = useState('')

  const mutation = useMutation({
    mutationFn: (data: any) => returnsApi.inspect(Number(id), data),
    onSuccess: () => {
      alert('Inspection saved!')
      navigate(`/returns/${id}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({
      return_request_id: Number(id),
      inspector_id: 1,
      finding,
      recommendation,
      notes,
      checklists: {},
      inspection_photos: [],
    })
  }

  return (
    <div>
      <h1>Inspection - Return #{id}</h1>
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Finding</label>
            <select value={finding} onChange={(e) => setFinding(e.target.value)}>
              <option value="ok">OK</option>
              <option value="cosmetic_defect">Cosmetic Defect</option>
              <option value="functional_defect">Functional Defect</option>
              <option value="wrong_item">Wrong Item</option>
            </select>
          </div>
          <div className="form-group">
            <label>Recommendation</label>
            <select value={recommendation} onChange={(e) => setRecommendation(e.target.value)}>
              <option value="restock">Restock</option>
              <option value="repair">Repair</option>
              <option value="scrap">Scrap</option>
              <option value="supplier_return">Return to Supplier</option>
              <option value="refund">Refund</option>
            </select>
          </div>
          <div className="form-group">
            <label>Notes</label>
            <textarea rows={4} value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>
          <button type="submit" className="btn btn-primary">Submit Inspection</button>
        </form>
      </div>
    </div>
  )
}
