var n=1,tot_cost=0;
var items = [];
//Instead of all these just use following function
function removeRow(td){
  var tr = td.closest("tr");
  var rowIndex = tr.rowIndex;
  //alert(rowIndex);
  tot_cost -= items.remove(rowIndex);
  $('#tot_cost').html("Total : Rs "+ tot_cost);
  tr.remove();
  n--;
}

function valueChanged(td,isBlur){
	var str=td.innerHTML;
	var count=Number(str);
	var remark="";
	var price="";
	
	if((str!="" && isNaN(count)) || (isBlur === true && isNaN(count)))
	{
		td.innerHTML="0";
		count=0;
	}
	if(!isNaN(count))
	{
		var tr = td.closest("tr");
		price = parseInt(tr.cells[2].innerHTML,10);
		remark = price + " X " + count + " = " + price*count;
		tr.cells[4].innerHTML=remark;
    var rowIndex = tr.rowIndex-1;
    tot_cost += items[rowIndex].changecount(count);
    $('#tot_cost').html("Total : Rs "+ tot_cost);
	}
	if(isBlur && count===0)
		td.innerHTML="0";
}
  
