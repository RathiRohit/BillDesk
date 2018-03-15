class Item{
	constructor(i_name,i_price,i_count){
		this._i_name = i_name;
		this._i_price = i_price;
		this._i_count = i_count;
		this._i_tot_price = parseInt(i_count)*parseInt(i_price);
	}
	getCount(){
		return this._i_count;
	}
	getName(){
		return this._i_name;
	}
	getItem(){
		return `${this._i_name} ${this._i_price} ${this._i_count} ${this._i_tot_price}`
	}
	changecount(cnt){
		var prev = this._i_tot_price;
		this._i_count = cnt;
		this._i_tot_price = parseInt(cnt)*parseInt(this._i_price);
		return (this._i_tot_price - prev);
	}
	get_totcost(){
		return this._i_tot_price;
	}
}
Array.prototype.insert = function(item){
	this.push(item);	
}	
Array.prototype.remove = function(i){
	var minus = this[i-1].get_totcost();
	this.splice(i-1,1);
	return minus;
}