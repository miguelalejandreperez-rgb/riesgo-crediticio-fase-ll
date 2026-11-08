'use strict';

const labels = {
  LIMIT_BAL: 'Límite de crédito',
  PAY_0: 'Estado período 1', PAY_2: 'Estado período 2', PAY_3: 'Estado período 3',
  PAY_4: 'Estado período 4', PAY_5: 'Estado período 5', PAY_6: 'Estado período 6',
};
const fields = [
  {target:'group-credit', names:['LIMIT_BAL']},
  {target:'group-status', names:['PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6']},
  {target:'group-bills', names:[1,2,3,4,5,6].map(i=>'BILL_AMT'+i)},
  {target:'group-payments', names:[1,2,3,4,5,6].map(i=>'PAY_AMT'+i)},
];
const example = {
  LIMIT_BAL: 120000,
  PAY_0: -1, PAY_2: 2, PAY_3: 0, PAY_4: 0, PAY_5: 0, PAY_6: 0,
  BILL_AMT1: 2682, BILL_AMT2: 1725, BILL_AMT3: 2682,
  BILL_AMT4: 3272, BILL_AMT5: 3455, BILL_AMT6: 3261,
  PAY_AMT1: 0, PAY_AMT2: 1000, PAY_AMT3: 1000,
  PAY_AMT4: 1000, PAY_AMT5: 0, PAY_AMT6: 2000,
};

for (const group of fields) {
  const container = document.getElementById(group.target);
  for (const name of group.names) {
    const label = document.createElement('label');
    label.className='field';
    const title = labels[name] || (name.startsWith('BILL_') ? `Factura ${name.at(-1)}` : `Pago ${name.at(-1)}`);
    const span = document.createElement('span');span.textContent = title;
    const input = document.createElement('input');
    input.name = name;input.type = 'number';input.required = true;input.step = name.startsWith('PAY_') && !name.startsWith('PAY_AMT') ? '1' : 'any';
    input.min = name === 'LIMIT_BAL' ? '0.01' : name.startsWith('PAY_') && !name.startsWith('PAY_AMT') ? '-2' : name.startsWith('PAY_AMT') ? '0' : '-1000000000';
    input.max = name.startsWith('PAY_') && !name.startsWith('PAY_AMT') ? '8' : '1000000000';
    input.value = String(example[name]);input.id=name;
    label.append(span,input);container.append(label);
  }
}

const form=document.getElementById('risk-form');
const result=document.getElementById('result-content');
const resultPanel=document.querySelector('.result');
const status=document.getElementById('model-status');
const run=document.getElementById('run');

async function checkHealth(){
  try{
    const response=await fetch('/api/health');
    if(!response.ok)throw new Error('Modelo aún no exportado o disponible');
    status.textContent='● Modelo disponible para inferencia';
  }catch(error){status.textContent='● Modelo no disponible: requiere entrenamiento/exportación';}
}
checkHealth();

document.getElementById('reset').addEventListener('click',()=>{
  for(const [name,value] of Object.entries(example))document.getElementById(name).value=value;
  resultPanel.classList.remove('ok','flag');
  result.innerHTML='<div class="placeholder-icon">%</div><h2>Sin evaluación</h2><p>Ejemplo restablecido. Presiona «Calcular puntuación».</p>';
});

form.addEventListener('submit',async event=>{
  event.preventDefault();
  if(!form.reportValidity())return;
  const payload={};
  for(const field of fields)for(const name of field.names){
    const value=document.getElementById(name).value.trim();
    if(value===''){return showError(`Falta completar ${name}.`);}
    payload[name]=Number(value);
  }
  run.disabled=true;run.textContent='Procesando...';
  try{
    const response=await fetch('/api/predecir',{
      method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)
    });
    const data=await response.json();
    if(!response.ok){
      const msg=Array.isArray(data.detail)?data.detail.map(x=>`${x.loc?.join('.')}: ${x.msg}`).join('; '):data.detail;
      throw new Error(msg||'Error inesperado');
    }
    resultPanel.classList.remove('ok','flag');resultPanel.classList.add(data.alerta?'flag':'ok');
    // Se construye el HTML únicamente con números y cadenas de etiquetas locales.
    const percentage=(data.puntaje_incumplimiento*100).toFixed(2);
    const threshold=(data.umbral_alerta*100).toFixed(0);
    result.innerHTML=`<div class="score">${percentage}%</div>
      <div class="score-subtitle">Puntuación experimental (no calibrada)</div>
      <div class="meter"><div class="meter-fill" style="width:${percentage}%"></div></div>
      <div class="status-label">${data.alerta?'Alerta activada':'Sin alerta'}</div>
      <p class="hint">Umbral aprendido en validación: ${threshold}%. Esta salida no implica aprobar ni rechazar un crédito.</p>`;
  }catch(error){showError(error.message)}
  finally{run.disabled=false;run.textContent='Calcular puntuación'}
});

function showError(message){
  resultPanel.classList.remove('ok','flag');
  result.innerHTML='';
  const h=document.createElement('h2');h.textContent='No se pudo evaluar';
  const p=document.createElement('p');p.className='error';p.textContent=message;
  result.append(h,p);
}
