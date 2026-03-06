import { useState } from 'react'

interface FilterProps {
    topN: number
    qualityPower: number
    isOpen: boolean
    onTopNChange: (topN: number) => void
    onQualityPowerChange: (qualityPower: number) => void
    onClose: () => void
}

export function Filter({ topN, qualityPower, isOpen, onTopNChange, onQualityPowerChange, onClose }: FilterProps) {
    const [localTopN, setLocalTopN] = useState(topN)
    const [localQP, setLocalQP] = useState(qualityPower)

    if (!isOpen) return null

    const handleApply = () => {
        onTopNChange(localTopN)
        onQualityPowerChange(localQP)
        onClose()
    }

    return (
        <div className="filter-overlay" onClick={onClose}>
            <div className="filter-modal" onClick={(e) => e.stopPropagation()}>
                <h3>Filters</h3>

                <div className="filter-field">
                    <label htmlFor="topn-slider">Number of recommendations</label>
                    <input
                        id="topn-slider"
                        type="range"
                        min={1}
                        max={50}
                        step={1}
                        value={localTopN}
                        onChange={(e) => setLocalTopN(Number(e.target.value))}
                    />
                    <span className="range-value">{localTopN}</span>
                </div>

                <div className="filter-field">
                    <label htmlFor="quality-slider">Review Quality Weight</label>
                    <input
                        id="quality-slider"
                        type="range"
                        min={0}
                        max={5}
                        step={0.1}
                        value={localQP}
                        onChange={(e) => setLocalQP(Number(e.target.value))}
                    />
                    <span className="range-value">{localQP.toFixed(1)}</span>
                </div>

                <button className="filter-apply" onClick={handleApply}>Apply</button>
            </div>
        </div>
    )
}