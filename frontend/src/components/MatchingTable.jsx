import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';
import { cn } from '../lib/utils';

export function MatchingTable({ refreshTrigger }) {
    const [items, setItems] = useState([]);
    const [filter, setFilter] = useState('all'); // 'all', 'matched', 'unmatched'
    const [loading, setLoading] = useState(false);
    const [manualMatchModalOpen, setManualMatchModalOpen] = useState(false);
    const [selectedItem, setSelectedItem] = useState(null);

    const fetchItems = async () => {
        setLoading(true);
        try {
            const url = filter === 'all'
                ? 'http://localhost:8000/api/results/'
                : `http://localhost:8000/api/results/?status=${filter}`;
            const res = await axios.get(url);
            setItems(res.data);
        } catch (err) {
            console.error("Failed to fetch matches", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
    }, [filter, refreshTrigger]);

    const openManualMatch = (item) => {
        setSelectedItem(item);
        setManualMatchModalOpen(true);
    };

    const StatusBadge = ({ isMatched, confidence, type }) => {
        if (!isMatched) {
            return (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    <XCircle className="w-3.5 h-3.5 mr-1" /> Нет совпадений
                </span>
            );
        }

        if (confidence === 100) {
            return (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Точное ({type})
                </span>
            );
        }

        return (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                <AlertCircle className="w-3.5 h-3.5 mr-1" /> Примерное {confidence}%
            </span>
        );
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
                <h3 className="font-semibold text-slate-800">Результаты сопоставления</h3>
                <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="text-sm border-slate-200 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 py-1.5 pl-3 pr-8"
                >
                    <option value="all">Все записи ({items.length})</option>
                    <option value="matched">Сопоставленные</option>
                    <option value="unmatched">Требуют внимания</option>
                </select>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Товар поставщика</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Цена</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Эталонная номенклатура (1С)</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Статус</th>
                            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Действие</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200">
                        {loading ? (
                            <tr><td colSpan="5" className="px-6 py-8 text-center text-slate-500 text-sm">Загрузка данных...</td></tr>
                        ) : items.length === 0 ? (
                            <tr><td colSpan="5" className="px-6 py-8 text-center text-slate-500 text-sm">Нет данных для отображения. Загрузите прайс-лист.</td></tr>
                        ) : (
                            items.map((item) => (
                                <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-slate-900">{item.name}</div>
                                        <div className="text-xs text-slate-500 mt-1">
                                            {item.barcode ? `ШК: ${item.barcode}` : ''} {item.article ? `| Арт: ${item.article}` : ''}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700">
                                        {item.price ? `${item.price} ₽` : '-'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {item.master_item ? (
                                            <div>
                                                <div className="text-sm text-slate-900">{item.master_item.name}</div>
                                                <div className="text-xs text-slate-500 mt-1">Код 1С: {item.master_item.code_1c}</div>
                                            </div>
                                        ) : (
                                            <span className="text-sm text-slate-400 italic">Не найдено</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <StatusBadge isMatched={item.is_matched} confidence={item.match_confidence} type={item.match_type} />
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button
                                            onClick={() => openManualMatch(item)}
                                            className={cn(
                                                "transition-colors",
                                                (!item.is_matched || item.match_confidence < 90) ? "text-blue-600 hover:text-blue-900 font-semibold" : "text-slate-400 hover:text-blue-600"
                                            )}
                                        >
                                            {item.is_matched ? "Изменить" : "Найти"}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {manualMatchModalOpen && selectedItem && (
                <ManualMatchModal
                    item={selectedItem}
                    onClose={() => setManualMatchModalOpen(false)}
                    onSuccess={() => {
                        setManualMatchModalOpen(false);
                        fetchItems();
                    }}
                />
            )}
        </div>
    );
}

function ManualMatchModal({ item, onClose, onSuccess }) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [searching, setSearching] = useState(false);

    useEffect(() => {
        // Initial search attempt with part of the name
        const initialWords = item.name.split(' ').slice(0, 3).join(' ');
        setQuery(initialWords);
        handleSearch(initialWords);
    }, [item]);

    const handleSearch = async (searchQuery) => {
        if (!searchQuery.trim()) return;
        setSearching(true);
        try {
            const res = await axios.get(`http://localhost:8000/api/search-master-items/?query=${encodeURIComponent(searchQuery)}`);
            setResults(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setSearching(false);
        }
    };

    const handleSelect = async (masterId) => {
        try {
            await axios.post(`http://localhost:8000/api/manual-match/${item.id}?master_item_id=${masterId}`);
            onSuccess();
        } catch (err) {
            console.error("Manual match failed", err);
            alert("Не удалось сохранить выбор");
        }
    };

    return (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl flex flex-col max-h-[90vh]">
                <div className="p-6 border-b border-slate-100">
                    <h3 className="text-xl font-semibold text-slate-800">Ручное сопоставление</h3>
                    <p className="text-sm text-slate-500 mt-1">Поставщик: {item.supplier_name}</p>
                </div>

                <div className="p-6 flex-1 overflow-hidden flex flex-col gap-6">
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                        <div className="text-sm text-slate-500 mb-1">Оригинальное название:</div>
                        <div className="font-medium text-slate-900 text-lg">{item.name}</div>
                        <div className="text-sm text-slate-600 mt-2 flex gap-4">
                            {item.barcode && <span>Штрихкод: <span className="font-mono bg-white px-1.5 py-0.5 rounded border">{item.barcode}</span></span>}
                            {item.article && <span>Артикул: <span className="font-mono bg-white px-1.5 py-0.5 rounded border">{item.article}</span></span>}
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <div className="relative flex-1">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search className="h-5 w-5 text-slate-400" />
                            </div>
                            <input
                                type="text"
                                className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                placeholder="Поиск по базе 1С (название, арт, шк)..."
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
                            />
                        </div>
                        <button
                            onClick={() => handleSearch(query)}
                            className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors"
                        >
                            Искать
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto border border-slate-200 rounded-xl">
                        {searching ? (
                            <div className="p-8 text-center text-slate-500">Поиск...</div>
                        ) : results.length === 0 ? (
                            <div className="p-8 text-center text-slate-500">Ничего не найдено. Попробуйте изменить запрос.</div>
                        ) : (
                            <ul className="divide-y divide-slate-100">
                                {results.map((r) => (
                                    <li key={r.id} className="p-4 hover:bg-blue-50 transition-colors flex items-center justify-between group">
                                        <div>
                                            <div className="font-medium text-slate-900">{r.name}</div>
                                            <div className="text-xs text-slate-500 mt-1 flex gap-3">
                                                <span>Код 1С: {r.code_1c}</span>
                                                {r.barcode && <span>ШК: {r.barcode}</span>}
                                                {r.article && <span>Арт: {r.article}</span>}
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleSelect(r.id)}
                                            className="opacity-0 group-hover:opacity-100 px-4 py-1.5 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-all"
                                        >
                                            Выбрать
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>

                <div className="p-4 border-t border-slate-100 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-5 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium transition-colors"
                    >
                        Отмена
                    </button>
                </div>
            </div>
        </div>
    );
}
