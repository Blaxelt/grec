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

    const handleClose = () => {
        setLocalTopN(topN)
        setLocalQP(qualityPower)
        onClose()
    }

    const handleApply = () => {
        onTopNChange(localTopN)
        onQualityPowerChange(localQP)
        onClose()
    }

    return (
        <div className="fixed inset-0 flex items-center justify-center bg-black/55 backdrop-blur-sm z-100"
            onClick={handleClose}>
            <div className="border border-border rounded-2xl p-6 bg-surface gap-2 flex flex-col w-80" onClick={(e) => e.stopPropagation()}>
                <h3 className="text-xl p-3 font-semibold">Filters</h3>

                <div className="text-text-dim flex flex-col gap-2 w-full p-3">
                    <label htmlFor="topn-slider">Number of recommendations</label>
                    <input
                        className='cursor-pointer accent-accent'
                        id="topn-slider"
                        type="range"
                        min={1}
                        max={50}
                        step={1}
                        value={localTopN}
                        onChange={(e) => setLocalTopN(Number(e.target.value))}
                    />
                    <span className="text-right text-accent">{localTopN}</span>
                </div>

                <div className="text-text-dim flex flex-col gap-2 w-full p-3">
                    <label htmlFor="quality-slider">Review Quality Weight</label>
                    <input
                        className='cursor-pointer accent-accent'
                        id="quality-slider"
                        type="range"
                        min={0}
                        max={5}
                        step={0.1}
                        value={localQP}
                        onChange={(e) => setLocalQP(Number(e.target.value))}
                    />
                    <span className="text-right text-accent">{localQP.toFixed(1)}</span>
                </div>

                <button className="border p-2 rounded-lg bg-accent border-accent cursor-pointer
                hover:bg-accent/80 hover:border-accent/80 hover:text-white font-semibold transition-all duration-150"
                    onClick={handleApply}>Apply</button>
            </div>
        </div>
    )
}