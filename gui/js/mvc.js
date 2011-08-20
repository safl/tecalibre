var mvc = {
    pager: function(perPage, data) {
        
        var self = this;
        
        self.cur_page = function() {
            return Math.ceil( (data.cur()+1) / perPage);
        }
        
        self.total_pages = function() {
            return Math.ceil(data.length / perPage);
        }
        
        self.total_elements = function() {
            return data.length;
        }
        
        self.elements = function() {
            
            var offset = (self.cur_page()-1)*perPage;
            
            $.log('Elements cur_page '+self.cur_page());
            $.log('Elements perpage '+perPage);
            $.log('Elements from index ['+offset+'] to ['+(offset+(perPage-1))+']');
            var ee = new Array();
            for(var i=offset; i<=offset+(perPage-1); i++) {
                $.log('Elements!!');
                if (i<data.length) {
                    ee.push(data.getItem(i));
                } else {
                    break;
                }
            }

            return ee;
        }
        
        return self;
        
    },
    
    dataSet: function(url, callback) {
    
        var i       = 0;
        var next    = 0;
        var prev    = 0;
        var data    = new Array();        
        var self    = this;
        
        var cb = callback;
        
        self.length = 0;
                
        self.load = function() {
            
            $.ajax({                    // Initialize
                dataType:   "json",
                url:        url,
                success: function (remoteData) {
                    
                                        // Remove null instances...
                    for(var j=0; j<remoteData.length; j++){
                        if (remoteData[j]){
                          data.push(remoteData[j]);
                      }
                    }
                    self.length = data.length;
                    cb(self);
                    
                }
            });
            
        }
        
        self.getRaw = function() {
            return data;
        }
    
        self.cur = function() {            
            return i;        
        }
        
        self.inc = function() {
            return (i < (data.length-1)) ? i + 1 : 0;
        }
        
        self.dec = function() {
            return (i>0) ?  i -= 1 : (data.length-1);
        }
        
        self.next = function() {
            i = (i < (data.length-1)) ? i + 1 : 0;
            return i;        
        }
        
        self.prev = function() {
            
            i = (i>0) ?  i -= 1 : (data.length-1)
            return i;
        }
        
        self.getItem = function(index) {            
            return (index>=0) ? data[index] : data[i];            
        }
        
        self.load();            // Load the data
        
        return self;
        
    },

    dataSource: function(database, collection) {
    
        var dsPrefix = '/pyremo';
    
        var db      = (database) ? database : 'media';
        var coll    = (collection) ? collection : 'movies';        
        var q_str   = dsPrefix+"/"+db+"/"+coll;
        
        var self = this;
        
        self.query = function( q ) {
            return dataSet( (q) ? q_str + q : q_str );
        }
        
        self.find = function(limit, sort) {
            
            var q = '/find//';
            
            if (limit || sort) {
                q += '?';
            }
            q += (limit) ? "limit="+limit : '';
            
            return self.query( q );
        }
        
        self.drop = function() {
            return self.query( '/drop' );
        }
        
        return self;
    },

    controller: function(name, template) {
        
        var self = this;
        var data   = [];
        
        self.assign = function(key, value) {
            data[key]= value;
        }
        
        self.render = function() {
            $(name).empty();
            $(template).tmpl({'data': data}).appendTo(name);
        }
        
        return self;
    
    }

}