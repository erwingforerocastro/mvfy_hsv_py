
class MvFyVisual:

    def __init__(self) -> None:
        """
         Main model builder
         @constructor
         @param {Object} args
         @param {*} args.server - Backend server for the websocket. 
         @param {Object} args.options - options for the websocket.
         @param {Any|Number} args.port - Server listen port.
         @param {String} args.type_service - type of the listen server.
         @param {Array} args.min_date_knowledge [min_date_knowledge=null] - minimum interval to determine a known user.
         @param {Number} args.min_frequency [min_frequency=0.7] - minimum frequency between days detectioned.
         @param {String} args.features [features=null] - characteristics that will be saved in each detection.
         @param {String} args.decoder [decoder='utf-8'] - data decoder.
         @param {String} args.max_descriptor_distance [max_descriptor_distance=null] - max distance of diference between detections.
         @param {String} args.type_system [type_system=null] - type of system.
         @param {String} args.title [title=null] - title of system.
        /
        """
        let { server, options, ...otherInfo } = args
        #create or return system of bd

        this._require_create = (otherInfo.type_service == constants.TYPE_SERVICE.LOCAL)
        this.type_service = otherInfo.type_service //*required
        this.port = otherInfo.port
        this.domain = "localhost"
        this.title = Math.floor(new Date() / 1000)
        this._stream_fps = 30
        this.id = null
        this.features = null
        this.min_date_knowledge = null
        this.min_frequency = 0.7
        this.decoder = 'utf-8'
        this.max_descriptor_distance = null
        this.type_system = null
        this.execution = false
        this.type_model_detection = null
        this.display_size = { width: 300, height: 300 }
        this.matches = null
        this.stream_video = null
        this.interval_streaming = null
        this._insert(otherInfo)

        if (server == null || options == null) {
            throw new Error("server and options argument is required")
        }

        this.io = SocketIO(server, options)

    def 